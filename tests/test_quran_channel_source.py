from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.models import QuranAssetKind
from khatmsaz.modules.content.quran_channel_seed import (
    AUDIO_MESSAGE_RANGES, IMAGE_MESSAGE_IDS, validate_seed,
)


def test_parse_quran_channel_caption_accepts_persian_page_formats():
    assert content_service.parse_quran_channel_caption("صفحه ۳") == (
        QuranAssetKind.IMAGE, 3, 3,
    )
    assert content_service.parse_quran_channel_caption("صفحات ۱ و ۲") == (
        QuranAssetKind.IMAGE, 1, 2,
    )
    assert content_service.parse_quran_channel_caption("صوت صفحات ۶۰۲ و ۶۰۳ و ۶۰۴") == (
        QuranAssetKind.AUDIO, 602, 604,
    )


def test_parse_quran_channel_caption_rejects_headings_and_non_contiguous_pages():
    assert content_service.parse_quran_channel_caption("#جزء ۳") is None
    assert content_service.parse_quran_channel_caption("صوت صفحات ۳ و ۵") is None
    assert content_service.parse_quran_channel_caption("صفحه ۶۰۵") is None


def test_telegram_forward_ref_round_trip():
    value = content_service.encode_telegram_forward_ref(-1001127138974, 1078)
    assert content_service.decode_telegram_forward_ref(value) == (-1001127138974, 1078)
    assert content_service.decode_telegram_forward_ref("ordinary-file-id") is None


def test_verified_channel_seed_covers_exactly_604_pages():
    validate_seed()
    assert len(IMAGE_MESSAGE_IDS) == 604
    audio_pages = {
        page for start, end, _message_id in AUDIO_MESSAGE_RANGES
        for page in range(start, end + 1)
    }
    assert audio_pages == set(range(1, 605))
    assert (254, 255, 492) in AUDIO_MESSAGE_RANGES
