from khatmsaz.modules.authorization.models import AdminRole
from khatmsaz.modules.khatm.models import KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.wallet.models import InvoiceKind, InvoiceStatus
from khatmsaz.web.app import _fa_label


def test_admin_visible_enums_have_persian_labels():
    assert _fa_label(KhatmStatus.ACTIVE) == "فعال"
    assert _fa_label(KhatmTemplateType.QURAN_PAGE) == "صفحات قرآن"
    assert _fa_label(KhatmTypeEnum.COMMITMENT) == "تعهدی"
    assert _fa_label(InvoiceKind.KHATM_CREATION) == "ساخت ختم"
    assert _fa_label(InvoiceStatus.REFUNDED) == "بازپرداخت‌شده"
    assert _fa_label(AdminRole.OPERATIONS_ADMIN) == "مدیر عملیات"
    assert _fa_label("ar") == "عربی"


def test_unknown_machine_value_is_made_readable_without_crashing():
    assert _fa_label("FUTURE_VALUE") == "FUTURE VALUE"
