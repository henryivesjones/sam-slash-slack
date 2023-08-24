from setuptools import setup

setup(
    url="https://github.com/henryivesjones/sam-slash-slack",
    packages=["sam_slash_slack"],
    package_dir={"sam_slash_slack": "sam_slash_slack"},
    package_data={"sam_slash_slack": ["py.typed"]},
    include_package_data=True,
)
