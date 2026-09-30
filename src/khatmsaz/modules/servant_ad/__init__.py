"""خدمتگزاران system promo ads (owner §A4).

Admin-defined promotional message delivered — admin-initiated, never on an
automatic timer — to the audiences of creators currently on the BASIC plan
(where `plan_service.ads_enabled_for_creator` is True). Stored in the generic
system-settings KV store (no migration); isolated so nothing else depends on it.
"""
