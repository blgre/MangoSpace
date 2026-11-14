import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import download_sme2


class DownloadCommandTest(unittest.TestCase):
    def test_manifest_query_and_empty_catalogue_fail_before_login(self):
        with (
            patch("sys.argv", ["download_sme2.py", "--search-only"]),
            patch.object(download_sme2.earthaccess, "search_data", return_value=[]) as search,
            patch.object(download_sme2.earthaccess, "login") as login,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            with self.assertRaisesRegex(SystemExit, "No matching SME2"):
                download_sme2.main()
        search.assert_called_once_with(
            short_name="NISAR_L3_SME2_PROVISIONAL_V1",
            bounding_box=(123.2, 9.4, 124.7, 11.4),
            temporal=("2026-06-21", "2026-10-31"),
            count=-1,
        )
        login.assert_not_called()

    def test_download_writes_actual_count_and_size(self):
        manifest = {"bounds": [123.2, 9.4, 124.7, 11.4], "windows": [{"start": "2026-06-21", "end": "2026-10-31"}]}
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "pipeline"
            root.mkdir()
            public = root.parent / "app/public/data"
            public.mkdir(parents=True)
            (public / "manifest.json").write_text(json.dumps(manifest))

            def download(results, local_path, show_progress):
                self.assertTrue(show_progress)
                path = Path(local_path) / "sample.h5"
                path.write_bytes(b"sample")
                return [str(path)]

            with (
                patch("sys.argv", ["download_sme2.py"]),
                patch.object(download_sme2, "ROOT", root),
                patch.object(download_sme2.earthaccess, "search_data", return_value=[{}]),
                patch.object(download_sme2.earthaccess, "login") as login,
                patch.object(download_sme2.earthaccess, "download", side_effect=download),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                login.return_value.authenticated = True
                download_sme2.main()
            summary = json.loads((root / "data/sme2/download-summary.json").read_text())
            self.assertEqual((summary["granules"], summary["files"], summary["bytes"]), (1, 1, 6))
            login.assert_called_once_with(persist=False)
