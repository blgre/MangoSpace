import { expect, test } from "@playwright/test";
import type { Target } from "../lib/data";

test("every Malinao Dam date has a water area and HH and HV images that load", async ({ page, request }) => {
  const targets: Target[] = await (await request.get("/data/targets.json")).json();
  const { dates, images, waterAreaKm2 } = targets.find((target) => target.id === "malinao-dam")!.nisar;
  expect(dates.length).toBeGreaterThan(0);
  expect(images).toHaveLength(dates.length);
  expect(waterAreaKm2).toHaveLength(dates.length);

  for (const path of images.flatMap((image) => [image.hh, image.hv])) {
    await page.goto(`/data/${path}`);
    const size = await page.evaluate(() => [document.images[0].naturalWidth, document.images[0].naturalHeight]);
    expect(size, path).toEqual([440, 440]);
  }
});
