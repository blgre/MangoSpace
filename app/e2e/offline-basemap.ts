import type { Page } from "@playwright/test";

export async function useOfflineBasemap(page: Page) {
  await page.route("https://tiles.openfreemap.org/**", (route) => route.fulfill({
    status: 200,
    contentType: "application/json",
    headers: { "access-control-allow-origin": "*" },
    body: JSON.stringify({
      version: 8,
      name: "Offline test basemap",
      sources: {},
      layers: [{
        id: "background",
        type: "background",
        paint: { "background-color": "#e7ece9" },
      }],
    }),
  }));
}
