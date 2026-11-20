import { test } from "node:test";
import assert from "node:assert/strict";
import { splitMessage, toCard, cleanCode, cleanOrder, cleanZip } from "../build-test/segments.mjs";

const fence = (lang, body) => "```" + lang + "\n" + body + "\n```";

test("markdown, a products card and suggestions", () => {
    const msg = "Here are two picks.\n\n" + fence("card", '{"type":"products","title":"Picks","codes":["PZ-01","pz-07"]}') + "\n\n" + fence("suggestions", '["What is vegan?","Deliver to 94110?"]');
    const s = splitMessage(msg);
    assert.deepEqual(s.map(x => x.kind), ["markdown", "cards", "suggestions"]);
    assert.deepEqual(s[1].cards[0].codes, ["PZ-01", "PZ-07"]);
    assert.deepEqual(s[2].items, ["What is vegan?", "Deliver to 94110?"]);
});

test("cards carry names, not markup: bad codes, ZIPs and orders are dropped", () => {
    assert.equal(cleanCode("<img src=x>"), undefined);
    assert.equal(cleanCode("PZ-01"), "PZ-01");
    assert.equal(cleanZip("9410"), undefined);
    assert.equal(cleanZip("94105"), "94105");
    assert.equal(cleanOrder("MX-1061"), "1061");
    assert.equal(cleanOrder("1061; drop"), undefined);
    assert.equal(toCard({ type: "products", codes: ["<b>"] }), undefined, "a products card without a valid code is not shown");
    assert.equal(toCard({ type: "zone", zip: "abc" }), undefined);
    assert.equal(toCard({ type: "order" }), undefined);
});

test("only known actions survive, with clamped quantities", () => {
    const c = toCard({ type: "info", title: "x", actions: [
        { label: "Add 2", action: "add", code: "PZ-01", quantity: 2 },
        { label: "Add many", action: "add", code: "PZ-02", quantity: 99 },
        { label: "Pay now", action: "pay" },
        { label: "Track", action: "track", order: "MX-1061" },
        { label: "Checkout", action: "checkout" }
    ] });
    assert.deepEqual(c.actions.map(a => [a.action, a.code ?? a.order ?? "", a.quantity ?? 0]), [["add", "PZ-01", 2], ["add", "PZ-02", 1], ["track", "1061", 0]]);
});

test("an unclosed card while streaming is pending; invalid JSON is left out", () => {
    assert.deepEqual(splitMessage("Hi\n```card\n{\"type\":\"cart\"").map(x => x.kind), ["markdown", "pending"]);
    const bad = splitMessage("A\n" + fence("card", "{not json}") + "\nB");
    assert.deepEqual(bad.map(x => x.kind), ["markdown"]);
    assert.ok(!bad[0].text.includes("not json"), "the invalid block is not shown as text");
});

test("cart, zone and order cards", () => {
    assert.equal(toCard({ type: "cart" }).type, "cart");
    assert.equal(toCard({ type: "zone", zip: "94110" }).zip, "94110");
    assert.equal(toCard({ type: "order", order: "MX-1077" }).order, "1077");
    assert.equal(toCard({ type: "product", code: "dr-01" }).codes[0], "DR-01", "a single product card is a products card");
});
