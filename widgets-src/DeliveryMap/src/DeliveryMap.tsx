import { ReactElement, useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { DeliveryMapContainerProps } from "../typings/DeliveryMapProps";
import { courierAt, LatLon, point } from "./components/geo";
import "./ui/DeliveryMap.css";

// The delivery map (US-097, SCR-06 and SCR-08): Leaflet on Esri's keyless Dark Gray
// Canvas basemap with its label layer, as in ako/ChatV2's map cards. The store, the
// destination zone, a dashed route with the distance, and the courier along it.
// Without tiles (offline) the simulated map image shows under the markers instead.
// Labels are set as text, never as HTML.

const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas";
const ATTRIBUTION = 'Tiles &copy; <a href="https://www.esri.com" target="_blank" rel="noopener">Esri</a> &mdash; Esri, HERE, Garmin, &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors';

type Num = { status: string; value?: { toNumber(): number } } | undefined;
type Str = { status: string; value?: string } | undefined;
const num = (v: Num): number | undefined => (v && v.status === "available" && v.value !== undefined ? v.value.toNumber() : undefined);
const str = (v: Str): string => (v && v.status === "available" && v.value ? v.value : "");

function pin(kind: "store" | "dest" | "courier", icon: string, label: string): L.DivIcon {
    const html = document.createElement("div");
    html.className = "gdm-pin-inner";
    const mk = document.createElement("span");
    mk.className = "gdm-mk";
    const ms = document.createElement("span");
    ms.className = "ms";
    ms.setAttribute("aria-hidden", "true");
    ms.textContent = icon;
    mk.append(ms);
    html.append(mk);
    if (label) {
        const nm = document.createElement("span");
        nm.className = "gdm-nm";
        nm.textContent = label;
        html.append(nm);
    }
    return L.divIcon({ className: `gdm-pin gdm-pin--${kind}`, html, iconSize: [34, 34], iconAnchor: [17, 17] });
}

function fit(lmap: L.Map, pts: LatLon[]): void {
    if (pts.length === 1) lmap.setView(pts[0], 14, { animate: false });
    else if (pts.length > 1) lmap.fitBounds(L.latLngBounds(pts), { padding: [48, 48], maxZoom: 15, animate: false });
}

export function DeliveryMap(props: DeliveryMapContainerProps): ReactElement {
    const box = useRef<HTMLDivElement>(null);
    const map = useRef<L.Map | undefined>(undefined);
    const layer = useRef<L.LayerGroup | undefined>(undefined);
    const fitted = useRef("");
    const points = useRef<LatLon[]>([]);
    const [offline, setOffline] = useState(false);

    const store = point(num(props.storeLat), num(props.storeLon));
    const dest = point(num(props.destLat), num(props.destLon));
    const courier = courierAt(store, dest, num(props.courierProgress));
    const storeLabel = str(props.storeLabel);
    const destLabel = str(props.destLabel);
    const distance = str(props.distanceText);

    // the map itself, once
    useEffect(() => {
        const el = box.current;
        if (!el) return;
        const lmap = L.map(el, { scrollWheelZoom: false, zoomControl: true, attributionControl: true, center: [37.765, -122.415], zoom: 13 });
        let loaded = 0;
        let failed = 0;
        const base = L.tileLayer(`${ESRI}/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}`, { maxZoom: 16, attribution: ATTRIBUTION });
        base.on("tileload", () => { loaded++; setOffline(false); });
        base.on("tileerror", () => { failed++; if (loaded === 0 && failed >= 2) setOffline(true); });
        base.addTo(lmap);
        L.tileLayer(`${ESRI}/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}`, { maxZoom: 16 }).addTo(lmap);
        lmap.on("click", () => lmap.scrollWheelZoom.enable());
        lmap.on("mouseout", () => lmap.scrollWheelZoom.disable());
        // the page may first lay the map out hidden or narrow: re-measure and refit on every size change
        const ro = new ResizeObserver(() => { lmap.invalidateSize(); fit(lmap, points.current); });
        ro.observe(el);
        map.current = lmap;
        layer.current = L.layerGroup().addTo(lmap);
        return () => { ro.disconnect(); lmap.remove(); map.current = undefined; };
    }, []);

    // markers, route and courier, whenever the values change
    const key = JSON.stringify([store, dest, courier, storeLabel, destLabel, distance]);
    useEffect(() => {
        const lmap = map.current;
        const group = layer.current;
        if (!lmap || !group) return;
        group.clearLayers();
        const pts: LatLon[] = [];
        if (store) {
            L.marker(store, { icon: pin("store", "local_pizza", storeLabel), title: storeLabel || "Store", keyboard: true }).addTo(group);
            pts.push(store);
        }
        if (store && dest) {
            // the theme's primary colour (Leaflet's own default is blue)
            const accent = (box.current && getComputedStyle(box.current).getPropertyValue("--primary").trim()) || "#ff9d00";
            const route = L.polyline([store, dest], { className: "gdm-route", color: accent, opacity: 0.9, weight: 3, dashArray: "6 6" }).addTo(group);
            if (distance) route.bindTooltip(distance, { permanent: true, direction: "right", offset: [14, 0], className: "gdm-distance" });
        }
        if (dest) {
            L.marker(dest, { icon: pin("dest", "location_on", destLabel), title: destLabel || "Destination", keyboard: true, zIndexOffset: 500 }).addTo(group);
            pts.push(dest);
        }
        if (courier) {
            L.marker(courier, { icon: pin("courier", "electric_moped", ""), title: "Courier", keyboard: false, zIndexOffset: 1000 }).addTo(group);
        }
        // fit only when the store or destination moved, so a courier update does not reset the user's zoom
        const where = JSON.stringify(pts);
        points.current = pts;
        if (where !== fitted.current) {
            fitted.current = where;
            lmap.invalidateSize();
            fit(lmap, pts);
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [key]);

    const fallback = props.fallbackImage ? `url("${props.fallbackImage.replace(/"/g, "")}")` : undefined;
    return (
        <div className={`gdm ${props.class ?? ""}${offline ? " gdm--offline" : ""}`} style={props.style}>
            <div ref={box} className="gdm-map" style={{ height: props.height || 260, backgroundImage: offline ? fallback : undefined }}
                role="region" aria-label={dest ? `Delivery map: ${storeLabel || "store"} to ${destLabel || "destination"}${distance ? ", " + distance : ""}` : "Delivery map"} />
            {offline && <p className="gdm-note">Map tiles could not be loaded; showing the simulated map.</p>}
        </div>
    );
}
