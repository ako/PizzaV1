# PizzaChat

<!-- mxcli-brain -->

Decisions anchored to the PizzaChat module. Loaded when PizzaChat is in play,
not otherwise.

## Pizza chat design: Agents Kit as in ako/ChatV2 (Conversational UI, Agent Editor agent PizzaChat.PizzaAssistant on Mendix Cloud GenAI, key via --constant PizzaChat.MxGenAIKey=@env:GENAI_TEXT_KEY, never in the model). The agent only reads with tools and proposes; changes happen on card buttons the guest presses. Cards name things (product codes, ZIP, order number) and the PizzaChatText widget fetches the facts from rest/pizzachat/v1 with the guest's session, so the model cannot show a made-up price, status or position. Per-visitor limit MessagesPerHour (30); chats older than a day are removed daily. Asked for by the product owner on 2026-11-20; not part of the PRD.

Anchors: `@PizzaChat.PizzaAssistant`, `@PizzaChat.PizzaChatApi`, `@PizzaChat.SUB_Usage_Allow`, `@PizzaChat.SE_ChatCleanup` · id `cd33b4` · 2026-11-20

## Conversational UI's streaming handler reads the session cookie by host name (XASSESSIONID only when the host contains localhost): a local run must be opened on http://localhost:8080, not 127.0.0.1, or every streamed answer shows Error (found in ako/ChatV2).

Anchors: `@PizzaChat.ChatContext_PizzaAssistant_ActionMicroflow` · id `147ba2` · 2026-11-20

## ChatUsage is a server-only per-visitor counter: no client access and no business key by design

Anchors: `@PizzaChat.ChatUsage` · id `b748b9` · 2026-11-20

Accepts lint `SEC001` on `@PizzaChat.ChatUsage`: server-only counter, read and written by SUB_Usage_Allow only
Accepts lint `ARCH003` on `@PizzaChat.ChatUsage`: one counter per user; the user association is its identity

## The chat's card views mirror the JSON the widget reads (rest/pizzachat/v1), so they hold as many attributes as the card shows

Anchors: `@PizzaChat.OrderView`, `@PizzaChat.ProductView` · id `de4a25` · 2026-11-20

Accepts lint `DESIGN001` on `@PizzaChat.OrderView`: a view of one JSON object for the card widget
Accepts lint `DESIGN001` on `@PizzaChat.ProductView`: a view of one JSON object for the card widget
