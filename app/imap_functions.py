import ssl
from email.message import EmailMessage
import email


def find_trash_folder(imap):
    """Find the trash folder on the IMAP server.
    Returns the folder name if found, None otherwise.
    """
    resp_code, directories = imap.list()
    print("IMAP List Response Code : {}".format(resp_code))

    trash_candidates = ["trash", "bin", "deleted", "papierkorb", "cestino", "corbeille"]

    for directory in directories:
        decoded = directory.decode("utf-8")
        print(decoded)
        # Folder name is usually after the last quoted separator or at the end.
        # Try parsing with quotes first, then fall back to splitting by separator.
        if '"' in decoded:
            directory_name = decoded.split('"')[-1].strip()
        else:
            # No quotes: format likely "(\\HasNoChildren) \".\" INBOX"
            parts = decoded.rsplit(" ", 1)
            directory_name = parts[-1].strip() if len(parts) > 1 else decoded.strip()

        # Case-insensitive check against trash candidates
        for candidate in trash_candidates:
            if candidate in directory_name.lower():
                print("Has Trash Folder: {}".format(directory_name))
                return directory_name

    return None


def delete_msg(imap, msg_num):
    resp_code, response = imap.store(str(msg_num), "+FLAGS", "\\Deleted")
    print("Response Code : {}".format(resp_code))
    if response and response[0] is not None:
        print("Response      : {}\n".format(response[0].decode()))

    resp_code, response = imap.expunge()
    print("Response Code : {}".format(resp_code))
    if response and response[0] is not None:
        print("Response      : {}\n".format(response[0].decode()))


def move_msg(imap, msg_num, src_folder, dst_folder):
    imap.select(mailbox=src_folder, readonly=False)

    try:
        # Copy Message to dst_folder
        resp_code, response = imap.copy(str(msg_num), dst_folder)
        print("Response Code : {}".format(resp_code))
        if response and response[0] is not None:
            print("Response      : {}".format(response[0].decode()))

        # Delete Message from src_folder
        resp_code, response = imap.store(str(msg_num), "+FLAGS", "\\Deleted")
        print("Response Code : {}".format(resp_code))
        if response and response[0] is not None:
            print("Response      : {}\n".format(response[0].decode()))

        # Expunge src_folder
        resp_code, response = imap.expunge()
        print("Response Code : {}".format(resp_code))
        if response and response[0] is not None:
            print("Response      : {}\n".format(response[0].decode()))

        return True

    except Exception as e:
        print("move_msg failed: {}".format(e))
        return False


def move_msg_to_trash(imap, msg_num, folder, del_pref):
    trash_folder = find_trash_folder(imap)

    imap.select(mailbox=folder, readonly=False)

    def _delete_safe(imap, msg_num):
        try:
            delete_msg(imap, msg_num)
            return True
        except Exception as e:
            print("Delete failed: {}".format(e))
            return False

    # If explicitly set to permanent delete, or already in trash, delete directly
    if del_pref == "delete":
        _delete_safe(imap, msg_num)
        return "Deleted"

    # If we're already in a trash-like folder or drafts, delete directly
    if trash_folder is not None and (
        folder == trash_folder or folder == "INBOX.Drafts"
    ):
        _delete_safe(imap, msg_num)
        return "Deleted"

    # Try to move to trash folder if one exists
    if trash_folder is not None:
        try:
            resp_code, response = imap.copy(str(msg_num), trash_folder)
            print("Response Code : {}".format(resp_code))
            if response and response[0] is not None:
                print("Response      : {}".format(response[0].decode()))

            _delete_safe(imap, msg_num)
            return "Trashed"
        except Exception as e:
            print("Copy to trash failed: {}".format(e))
            _delete_safe(imap, msg_num)
            return "Deleted"

    # No trash folder found — fall back to permanent deletion
    _delete_safe(imap, msg_num)
    return "Deleted"


def sort_folders(imap):
    # List directories
    resp_code, directories = imap.list()

    folders = {}

    # Pull out folder names and number of messages.
    for directory in directories:
        directory_name = directory.decode().split('"')[-1].strip()
        try:
            resp_code, mail_count = imap.select(mailbox=directory_name, readonly=True)
            folders.update({directory_name: str(mail_count[0], "utf-8")})
        except:
            print(f"Cannot get number of messages for: {directory_name}")

    sorted_folders = {}

    for key in sorted(folders.keys()):
        sorted_folders.update({key: folders[key]})

    return sorted_folders


def message_list(imap, folder, id_list):
    # Select all mailbox information.
    imap.select(str(folder), readonly=True)

    # Initialize empty messages list.
    messages = []
    for i in id_list:
        try:
            typ, msg_data = imap.fetch(str(i), "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    messages.insert(
                        0, [i, str(msg["from"]), str(msg["subject"]), str(msg["date"])]
                    )
        except:
            pass

    return messages


def get_msg_body_string(msg):
    msg_string_header = (
        f"From: {msg['from']}\nDate: {msg['date']}\nSubject: {msg['subject']}\n\n"
    )

    if msg.get_content_type() == "text/plain":
        return msg_string_header + msg.get_payload()

    for parte in msg.walk():
        if parte.get_content_type() == "text/plain":
            return msg_string_header + str(parte)


def get_msg_body(imap, msg_num, folder):
    imap.select(str(folder), readonly=True)
    resp_code, msg_data = imap.fetch(str(msg_num), "(RFC822)")  ## Fetch mail data.
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg_bytes = response_part[1]
            msg = email.message_from_bytes(msg_bytes)
            return get_msg_body_string(msg)


def get_id_list(imap, folder):
    # Select all mailbox information.
    imap.select(str(folder), readonly=True)

    type, data = imap.search(None, "ALL")
    mail_ids = data[0].decode("utf-8")
    id_list = mail_ids.split()
    return id_list
