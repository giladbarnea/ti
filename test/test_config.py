from test.testutils import assert_doesnt_raise
def test__sanity():
    with assert_doesnt_raise():
        from timefred.config import config