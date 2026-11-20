// Pure helpers for the delivery map, kept apart from Leaflet so they can be tested in node.

export type LatLon = [number, number];

/** A usable coordinate pair: both numbers finite and not the 0/0 "none" marker. */
export function point(lat: number | undefined, lon: number | undefined): LatLon | undefined {
    if (lat === undefined || lon === undefined || !Number.isFinite(lat) || !Number.isFinite(lon)) return undefined;
    if (lat === 0 && lon === 0) return undefined;
    if (Math.abs(lat) > 90 || Math.abs(lon) > 180) return undefined;
    return [lat, lon];
}

/** The position a fraction t (clamped to 0..1) of the way from a to b. */
export function along(a: LatLon, b: LatLon, t: number): LatLon {
    const f = Math.min(1, Math.max(0, t));
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
}

/** The courier's position, or undefined when there is no route or no progress to show (progress below 0). */
export function courierAt(store: LatLon | undefined, dest: LatLon | undefined, progress: number | undefined): LatLon | undefined {
    if (!store || !dest || progress === undefined || !Number.isFinite(progress) || progress < 0) return undefined;
    return along(store, dest, progress);
}
