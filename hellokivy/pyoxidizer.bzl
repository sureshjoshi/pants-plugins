def make_exe():
    dist = default_python_distribution()

    policy = dist.make_python_packaging_policy()

    # Note: Adding this for pydanic (unable to load from memory error otherwise)
    # https://pyoxidizer.readthedocs.io/en/stable/pyoxidizer_packaging_additional_files.html#packaging-installing-resources-on-the-filesystem
    # https://github.com/indygreg/PyOxidizer/issues/438
    policy.resources_location_fallback = "filesystem-relative:lib"

    python_config = dist.make_python_interpreter_config()
    python_config.run_module = "hellokivy.main"

    exe = dist.to_python_executable(
        name="hellokivy",
        packaging_policy=policy,
        config=python_config,
    )

    for resource in exe.pip_install(["kivy"]):
        resource.add_location = "filesystem-relative:lib"
        exe.add_python_resource(resource)

    # Recursively scan the filesystem at 'path' and grab matching 'packages'
    exe.add_python_resources(
        exe.read_package_root(
            path=".",
            packages=["hellokivy"],
        )
    )
    return exe


def make_embedded_resources(exe):
    return exe.to_embedded_resources()


def make_install(exe):
    # Create an object that represents our installed application file layout.
    files = FileManifest()
    # Add the generated executable to our install layout in the root directory.
    files.add_python_resource(".", exe)
    return files


register_target("exe", make_exe)
register_target(
    "resources", make_embedded_resources, depends=["exe"], default_build_script=True
)
register_target("install", make_install, depends=["exe"], default=True)

resolve_targets()
