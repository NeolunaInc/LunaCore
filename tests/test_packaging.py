import os
import tempfile
from unittest.mock import patch

import pytest

from agents.packaging.packager import PackagerAgent


class TestPackagerAgent:
    def test_create_zip_archive(self):
        agent = PackagerAgent()
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy file in temp_dir
            dummy_file = os.path.join(temp_dir, "test.txt")
            with open(dummy_file, "w") as f:
                f.write("test content")

            output_zip = os.path.join(temp_dir, "output.zip")
            result = agent.create_zip_archive(temp_dir, output_zip)
            assert "ZIP archive created" in result
            assert os.path.exists(output_zip)

    def test_create_zip_archive_nonexistent_path(self):
        agent = PackagerAgent()
        with pytest.raises(FileNotFoundError):
            agent.create_zip_archive("/nonexistent/path", "/tmp/test.zip")

    @patch("agents.packaging.packager.print")
    def test_generate_sbom(self, mock_print):
        agent = PackagerAgent()
        sbom = agent.generate_sbom("/fake/path")
        assert "version" in sbom
        assert "components" in sbom
        mock_print.assert_called_once_with("SBOM generated for /fake/path")

    def test_create_docker_image_no_dockerfile(self):
        agent = PackagerAgent()
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError):
                agent.create_docker_image(temp_dir, "test-image")

    @patch("agents.packaging.packager.print")
    def test_create_docker_image_with_dockerfile(self, mock_print):
        agent = PackagerAgent()
        with tempfile.TemporaryDirectory() as temp_dir:
            dockerfile = os.path.join(temp_dir, "Dockerfile")
            with open(dockerfile, "w") as f:
                f.write("FROM python:3.9\n")

            result = agent.create_docker_image(temp_dir, "test-image")
            assert "Image test-image built successfully" in result
            mock_print.assert_called_once_with(f"Building Docker image test-image from {temp_dir}")
