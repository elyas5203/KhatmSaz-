"""Import every module's models so they register on `Base.metadata`.

Alembic's `env.py` imports this single module to discover the full schema —
no module can be silently missing from a migration because it was forgotten
in a per-module import list.
"""

from khatmsaz.modules.account_merge import models as _account_merge_models  # noqa: F401
from khatmsaz.modules.audit_log import models as _audit_log_models  # noqa: F401
from khatmsaz.modules.content import models as _content_models  # noqa: F401
from khatmsaz.modules.broadcast import models as _broadcast_models  # noqa: F401
from khatmsaz.modules.allocation import models as _allocation_models  # noqa: F401
from khatmsaz.modules.advertising import models as _advertising_models  # noqa: F401
from khatmsaz.modules.authorization import models as _authorization_models  # noqa: F401
from khatmsaz.modules.identity import models as _identity_models  # noqa: F401
from khatmsaz.modules.invitation import models as _invitation_models  # noqa: F401
from khatmsaz.modules.khatm import models as _khatm_models  # noqa: F401
from khatmsaz.modules.khatm_category import models as _khatm_category_models  # noqa: F401
from khatmsaz.modules.khatm_request import models as _khatm_request_models  # noqa: F401
from khatmsaz.modules.message_template import models as _message_template_models  # noqa: F401
from khatmsaz.modules.manual_phone_verification import models as _manual_phone_verification_models  # noqa: F401
from khatmsaz.modules.notification import models as _notification_models  # noqa: F401
from khatmsaz.modules.open_contribution import models as _open_contribution_models  # noqa: F401
from khatmsaz.modules.participation import models as _participation_models  # noqa: F401
from khatmsaz.modules.phone import models as _phone_models  # noqa: F401
from khatmsaz.modules.plan import models as _plan_models  # noqa: F401
from khatmsaz.modules.session import models as _session_models  # noqa: F401
from khatmsaz.modules.settings import models as _settings_models  # noqa: F401
from khatmsaz.modules.waiting_list import models as _waiting_list_models  # noqa: F401
from khatmsaz.modules.wallet import models as _wallet_models  # noqa: F401
from khatmsaz.modules.bot_registry import models as _bot_registry_models  # noqa: F401
