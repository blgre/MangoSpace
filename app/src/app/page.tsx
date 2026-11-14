import { readFile } from "node:fs/promises";
import path from "node:path";
import type { Lgu, Manifest, Outlook } from "../../lib/data";
import Explorer from "./Explorer";

// ponytail: build-time read, no runtime validation. The Playwright smoke spec is the check.
async function load<T>(file: string): Promise<T> {
  return JSON.parse(await readFile(path.join(process.cwd(), "public/data", file), "utf8"));
}

export default async function Page() {
  const [manifest, lgus, outlooks] = await Promise.all([
    load<Manifest>("manifest.json"),
    load<Lgu[]>("lgus.json"),
    load<Outlook[]>("outlook.json"),
  ]);
  return <Explorer manifest={manifest} lgus={lgus} outlooks={outlooks} />;
}
