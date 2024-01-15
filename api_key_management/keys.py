import os
import cmd
from supabase import create_client, Client
import secrets

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def generate_api_key(length=32):
    """
    Generates a random API key.

    Parameters:
    length (int): Length of the API key to be generated.

    Returns:
    str: A randomly generated API key.
    """
    return secrets.token_hex(length)


class Ecommerce(cmd.Cmd):
    intro: str = "Welcome to the Ecommerce shell. Type help or ? to list commands.\n"
    prompt: str = "(Ecommerce) "

    def do_create_api_key(self, arg):
        'Creates a new API key'
        """
        Creates a new API key.

        Parameters:
        arg (str): The name of the API key to be created.

        Returns:
        str: A message indicating the API key has been created.
        """

        api_key = generate_api_key()
        data, count = supabase.table("api_keys").insert({"api_key": api_key}).execute()
        print(f"API key {api_key} has been created.")
    
    def do_get_active_api_keys(self, arg):
        'Gets all active API keys'
        """
        Gets all active API keys.

        Returns:
        str: A list of all active API keys.
        """

        data, count = supabase.table("api_keys").select("*").eq("active", True).execute()
        print(data, count)

if __name__ == '__main__':
    Ecommerce().cmdloop()