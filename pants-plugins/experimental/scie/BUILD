# Copyright 2023 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

python_sources()

python_distribution(
    name="scie-dist",
    dependencies=[":scie"],
    repositories=["@pypi"],  # Configuration in ~/.pypirc
    wheel=True,
    sdist=False,
    provides=python_artifact(
        name="robotpajamas.pants.scie",
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3 :: Only",
            "Topic :: Software Development :: Build Tools",
        ],
        description="A Pants plugin adding support for packaging SCIE.",
        keywords=["pants", "pants-plugin", "scie"],
        license="Apache License, Version 2.0",
        long_description_content_type="text/markdown",
        long_description=open("pants-plugins/experimental/scie/README.md").read(),
        project_urls={
            "Documentation": "https://github.com/sureshjoshi/pants-plugins",
            "Source": "https://github.com/sureshjoshi/pants-plugins",
            "Tracker": "https://github.com/sureshjoshi/pants-plugins/issues",
            "Changelog": "https://github.com/sureshjoshi/pants-plugins/blob/main/pants-plugins/experimental/scie/CHANGELOG.md",
        },
        version="0.1.1",
    ),
)
