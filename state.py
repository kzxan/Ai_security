import time
import os

events = []
last_image_path = None
system_started_at = time.time()


def add_event(event_type, count=0, image_path=None):
    global last_image_path

    events.append({
        "type": event_type,
        "count": count,
        "time": time.time()
    })

    if image_path:
        last_image_path = image_path

    cleanup_events()


def cleanup_events():
    global events
    now = time.time()
    events = [e for e in events if now - e["time"] <= 300]


def get_recent_events():
    cleanup_events()
    return events


def get_status_text():
    recent = get_recent_events()

    if not recent:
        return "✅ Соңғы 5 минутта тыныш. Қауіп анықталған жоқ."

    weapon_count = sum(1 for e in recent if e["type"] == "weapon")
    unknown_count = sum(1 for e in recent if e["type"] == "unknown")

    lines = [f"⚠️ Соңғы 5 минутта {len(recent)} оқиға тіркелді."]

    if weapon_count:
        lines.append(f"🔫 Қару анықталуы: {weapon_count}")
    if unknown_count:
        lines.append(f"👤 Бейтаныс адам: {unknown_count}")

    return "\n".join(lines)


def get_system_uptime_text():
    seconds = int(time.time() - system_started_at)
    minutes = seconds // 60
    hours = minutes // 60

    if hours > 0:
        return f"🟢 Жүйе жұмыс істеп тұр. Uptime: {hours} сағ {minutes % 60} мин"
    if minutes > 0:
        return f"🟢 Жүйе жұмыс істеп тұр. Uptime: {minutes} мин"
    return f"🟢 Жүйе жұмыс істеп тұр. Uptime: {seconds} сек"


def get_last_image_path():
    global last_image_path
    if last_image_path and os.path.exists(last_image_path):
        return last_image_path
    return None


def get_summary_text():
    recent = get_recent_events()
    if not recent:
        return "📊 Соңғы 5 минут: тыныш."

    weapon_count = sum(1 for e in recent if e["type"] == "weapon")
    unknown_count = sum(1 for e in recent if e["type"] == "unknown")
    max_people = max((e["count"] for e in recent), default=0)

    return (
        f"📊 Соңғы 5 минут қорытындысы:\n"
        f"— Оқиға саны: {len(recent)}\n"
        f"— Қару: {weapon_count}\n"
        f"— Бейтаныс адам: {unknown_count}\n"
        f"— Ең көп адам саны: {max_people}"
    )