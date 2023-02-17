import schemathesis

from config import basedir

schema = schemathesis.from_file(basedir / "documentation/open_api3_spec.yaml")


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
