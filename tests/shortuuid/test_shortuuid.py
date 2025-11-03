from iden.shortuuid import generator

def test_shortuuid():
    """
    Tests that a shortuuid can be generated.
    """
    suuid = generator.shortuuid()
    assert isinstance(suuid, str)
    assert len(suuid) > 10
