"""Legacy DB field remains compatible, but skip-today has no active API."""

from khatmsaz.modules.khatm import repository, service
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.modules.khatm_workflow import service as workflow_service


def test_skip_today_is_inert_and_defaults_off():
    assert Khatm.allow_skip_today.property.columns[0].default.arg is False
    assert repository.create.__kwdefaults__["allow_skip_today"] is False
    assert not hasattr(repository, "set_allow_skip_today")
    assert not hasattr(service, "set_allow_skip_today")
    assert not hasattr(workflow_service, "skip_today")
