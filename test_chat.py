import pytchat

# pytchat.create() ne type döndürüyor?
# Dummy video ID ile test (yaşlı olmayacak)
try:
    # Real example
    chat = pytchat.create(video_id="dQw4w9WgXcQ")  # Geçerli bir video
    print(f"Chat object type: {type(chat)}")
    print(f"Chat object methods:")
    methods = [m for m in dir(chat) if not m.startswith('_')]
    for m in methods:
        print(f"  - {m}")
except Exception as e:
    print(f"Error: {e}")

