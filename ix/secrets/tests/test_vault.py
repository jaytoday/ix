import textwrap
import hvac

import pytest
from hvac.exceptions import InvalidPath
from django.conf import settings

from ix.secrets import vault
from ix.secrets.vault import (
    get_token_store_client,
    create_user_policy,
    get_client,
    create_user_token,
    set_user_token,
    get_user_token,
    handle_new_user,
    UserVaultClient,
    delete_secrets_recursive,
)

TOKEN = "test_token"
DATA = {"key": "value"}
DATA2 = {"key": "value2"}


@pytest.mark.skip()
class TestSecretsFixtures:
    def test_delete_secrets_recursive(self):
        """Sanity checking fixture to make sure it deletes secrets correctly"""
        client = vault.get_root_client()

        # Create some test secrets
        secrets = {
            "delete_test": {"value": "value1"},
            f"{settings.VAULT_BASE_PATH}/secret1": {"value": "value1"},
            f"{settings.VAULT_BASE_PATH}/level1/secret2": {"value": "value2"},
            f"{settings.VAULT_BASE_PATH}/level2/b/secret3": {"value": "value3"},
        }
        for secret_path, secret_value in secrets.items():
            client.secrets.kv.v2.create_or_update_secret(
                path=secret_path, secret=secret_value
            )

        # Verify that the secrets exist
        list_response = client.secrets.kv.v2.list_secrets(path=settings.VAULT_BASE_PATH)
        assert "keys" in list_response["data"]
        assert "secret1" in list_response["data"]["keys"]
        assert "level1/" in list_response["data"]["keys"]
        assert "level2/" in list_response["data"]["keys"]

        # Call the function to delete the secrets
        delete_secrets_recursive(settings.VAULT_BASE_PATH)

        # Verify that the secrets have been deleted
        try:
            response = client.secrets.kv.v2.list_secrets(path=settings.VAULT_BASE_PATH)
        except InvalidPath:
            # it should raise because it should be empty
            pass
        else:
            # if it doesn't raise, we fail and report what keys are present
            assert False, response

        # values outside the base path should not be deleted
        response = client.secrets.kv.v2.list_secrets(path="")
        assert "delete_test" in response["data"]["keys"]

        # Calling the function when there are no secrets should not raise an error.
        delete_secrets_recursive(settings.VAULT_BASE_PATH)


@pytest.mark.skip()
@pytest.mark.django_db
@pytest.mark.usefixtures("clean_vault")
class TestVaultIntegration:
    @pytest.fixture(autouse=True)
    def setup_teardown(self, user):
        yield

        # Cleanup
        # For example, if you want to delete all the policies/tokens you created during tests.

        # Delete the user policy
        policy_name = f"user_{user.id}_policy"
        vault_client = get_token_store_client()
        vault_client.sys.delete_policy(policy_name)

        # Delete user token (If stored)
        try:
            vault_client.secrets.kv.v2.delete_metadata_and_all_versions(
                f"{settings.VAULT_BASE_PATH}/users/{user.id}/token"
            )
        except:  # noqa E722
            pass

    def test_get_token_store_client(self):
        client = get_token_store_client()
        assert client is not None

    def test_get_client(self):
        client = get_client(TOKEN)
        assert client is not None

    def test_create_user_policy(self, user):
        # 1. Call the create_user_policy function
        create_user_policy(user.id)

        # 2. Use the hvac client to read the policy from Vault
        vault_client = get_token_store_client()
        policy_name = f"user_{user.id}_policy"
        stored_policy = vault_client.sys.read_policy(policy_name)

        # Ensure the policy data was fetched
        assert stored_policy is not None

        # 3. Assert that the policy content matches the expected content
        expected_policy = textwrap.dedent(
            f"""
            # Allow user to read their own token
            path "secret/data/{settings.VAULT_BASE_PATH}/users/{user.id}/token" {{
                capabilities = ["read"]
            }}

            # Allow user to perform CRUD operations on arbitrary keys
            path "secret/data/{settings.VAULT_BASE_PATH}/users/{user.id}/keys/*" {{
                capabilities = ["create", "read", "update", "delete"]
            }}
            path "secret/metadata/{settings.VAULT_BASE_PATH}/users/{user.id}/keys/*" {{
                capabilities = ["read", "delete"]
            }}
            path "secret/destroy/{settings.VAULT_BASE_PATH}/users/{user.id}/keys/*" {{
                capabilities = ["update"]
            }}
        """
        )

        stored_lines = [
            line.strip() for line in stored_policy["rules"].splitlines() if line.strip()
        ]
        expected_lines = [
            line.strip() for line in expected_policy.splitlines() if line.strip()
        ]
        assert stored_lines == expected_lines

    def test_create_user_token(self, user):
        # 1. Call the create_user_token function
        token = create_user_token(user.id)
        assert token is not None

        # 2. Use the hvac client to validate the token exists in Vault
        vault_client = get_token_store_client()
        stored_token_data = vault_client.secrets.kv.v2.read_secret_version(
            f"{settings.VAULT_BASE_PATH}/users/{user.id}/token"
        )

        # Ensure the token data was fetched and extract the token from the nested dictionary
        assert stored_token_data is not None
        stored_token = stored_token_data["data"]["data"]["token"]
        assert stored_token == token

        # 3. Optionally, verify the token's TTL or other properties
        # Note: The below step is an example. The actual TTL retrieval might differ based on your Vault setup and version.
        # token_lookup = vault_client.auth.token.lookup(token)
        # assert token_lookup['data']['ttl'] <= 3600  # for 1h TTL, it's represented in seconds

    def test_get_user_token(self, user):
        vault_client = get_token_store_client()
        path = f"{settings.VAULT_BASE_PATH}/users/{user.id}/token"
        try:
            existing_token_data = vault_client.secrets.kv.v2.read_secret_version(path)
            assert existing_token_data is None
        except InvalidPath:
            pass

        # Gets token if it does not exist
        token = get_user_token(user.id)
        assert token is not None

        # returns it if it exists
        token2 = get_user_token(user.id)
        assert token == token2

    def test_set_user_token(self, user):
        # 1. Call the set_user_token function
        set_user_token(user.id, TOKEN)

        # 2. Use the hvac client to read the stored token from Vault
        vault_client = get_token_store_client()
        stored_token_data = vault_client.secrets.kv.v2.read_secret_version(
            f"{settings.VAULT_BASE_PATH}/users/{user.id}/token"
        )

        # Ensure the token data was fetched and extract the token from the nested dictionary
        assert stored_token_data is not None
        stored_token = stored_token_data["data"]["data"]["token"]

        # 3. Assert that the stored token matches the test token
        assert stored_token == TOKEN

    def test_handle_new_user(self, user):
        token = handle_new_user(user.id)
        assert token is not None

    def test_user_vault_client(self, user):
        """Test the UserVaultClient class

        client should be able to read/write/delete data to the user's Vault
        """
        path = "test_path_1"  # replace with your desired path
        client = UserVaultClient(user)
        assert client.base_path == f"{settings.VAULT_BASE_PATH}/users/{user.id}/keys"

        # sanity check secret doesn't exist yet
        with pytest.raises(hvac.exceptions.InvalidPath):
            client.read(path)

        # read / write
        client.write(path, DATA)
        read_data = client.read(path)
        assert DATA == read_data

        # write (update)
        client.write(path, DATA2)
        read_data = client.read(path)
        assert DATA2 == read_data

        # delete
        client.delete(path)
        with pytest.raises(hvac.exceptions.InvalidPath):
            client.read(path)

    def test_user_vault_client_with_token(self, user):
        """Test the UserVaultClient class.

        The client should be able to read/write data to the user's Vault.
        """
        path = "test_path_2"
        user_token = handle_new_user(user.id)
        client_with_token = UserVaultClient(user, token=user_token)
        client_with_token.write(path, DATA)
        read_data_with_token = client_with_token.read(path)
        assert DATA == read_data_with_token
