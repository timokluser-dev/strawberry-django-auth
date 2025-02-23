from django.contrib.auth import get_user_model
from strawberry.types import Info

from gqlauth.core.directives import HasPermission, IsAuthenticated, IsVerified
from gqlauth.core.types_ import GQLAuthErrors
from tests.testCases import AbstractTestCase, ArgTestCase, AsyncArgTestCase

USER_MODEL = get_user_model()


class DottedDict(dict):
    def __getattr__(self, item):
        return self.__getitem__(item)


def fake_info(user) -> Info:
    res = DottedDict(
        {"context": DottedDict({"user": user}), "path": DottedDict({"key": "some field"})}
    )
    return res


class TestAuthDirectives(ArgTestCase):
    def test_is_authenticated_fails(self):
        res = IsAuthenticated().resolve_permission(None, fake_info(None), None, None)
        assert res.code == GQLAuthErrors.UNAUTHENTICATED
        assert res.message == GQLAuthErrors.UNAUTHENTICATED.value

    def test_is_authenticated_success(self, db_verified_user_status):
        assert (
            IsAuthenticated().resolve_permission(
                None, fake_info(db_verified_user_status.user.obj), None, None
            )
            is None
        )

    def test_is_verified_fails(self, db_unverified_user_status):
        res = IsVerified().resolve_permission(
            None, fake_info(db_unverified_user_status.user.obj), None, None
        )
        assert res.code == GQLAuthErrors.NOT_VERIFIED
        assert res.message == GQLAuthErrors.NOT_VERIFIED.value

    def test_is_verified_success(self, db_verified_user_status):
        assert (
            IsVerified().resolve_permission(
                None,
                fake_info(db_verified_user_status.user.obj),
                None,
                None,
            )
            is None
        )

    def test_has_permission_fails(self, db_verified_user_status):
        user = db_verified_user_status.user.obj
        perm = HasPermission(
            permissions=[
                "sample.can_eat",
            ]
        )

        assert (
            perm.resolve_permission(None, fake_info(user), None, None).code
            is GQLAuthErrors.NO_SUFFICIENT_PERMISSIONS
        )

    def test_has_permission_success(self, db_verified_user_status_can_eat):
        user = db_verified_user_status_can_eat.user.obj
        perm = HasPermission(
            permissions=[
                "sample.can_eat",
            ]
        )
        assert perm.resolve_permission(None, fake_info(user), None, None) is None


class IsVerifiedDirectivesInSchemaMixin(AbstractTestCase):
    def make_query(self) -> str:
        return """
        query MyQuery {
          authEntry {
            ... on GQLAuthError {
              code
              message
            }
            ... on AuthQueries {
              apple {
                ... on AppleType {
                    color
                    isEaten
                    name
                }
                ... on GQLAuthError {
                  message
                  code
                }
              }
            }
          }
        }
        """

    def test_not_verified_fails(
        self, db_apple, db_unverified_user_status, allow_login_not_verified
    ):
        res = self.make_request(query=self.make_query(), user_status=db_unverified_user_status)
        assert res["apple"]["message"] == GQLAuthErrors.NOT_VERIFIED.value

    def test_verified_success(self, db_apple, db_verified_user_status):
        res = self.make_request(query=self.make_query(), user_status=db_verified_user_status)
        assert res["apple"] == {
            "color": db_apple.color,
            "isEaten": db_apple.is_eaten,
            "name": db_apple.name,
        }


class TestIsVerifiedDirectivesInSchema(IsVerifiedDirectivesInSchemaMixin, ArgTestCase):
    ...


class TestIsVerifiedDirectivesInSchemaAsync(IsVerifiedDirectivesInSchemaMixin, AsyncArgTestCase):
    ...


class HasPermissionDirectiveInSchemaMixin(AbstractTestCase):
    def make_query(self, apple_id):
        return (
            """
            mutation MyMutation {
              authEntry {
                ... on AuthMutation {
                  eatApple(appleId: %s) {
                    ... on AppleType {
                      color
                      isEaten
                      name
                    }
                    ... on GQLAuthError {
                      message
                      code
                    }
                  }
                }
                ... on GQLAuthError {
                  message
                  code
                }
              }
            }
                """
            % apple_id
        )

    def test_has_permission_fails(self, db_apple, db_verified_user_status):
        username = db_verified_user_status.user.username_field
        res = self.make_request(self.make_query(db_apple.id), db_verified_user_status)
        assert res["eatApple"] == {
            "code": "NO_SUFFICIENT_PERMISSIONS",
            "message": f"User {username}, has not " "sufficient permissions for " "eatApple",
        }

    def test_has_permission_success(self, db_apple, db_verified_user_status_can_eat):
        res = self.make_request(self.make_query(db_apple.id), db_verified_user_status_can_eat)
        assert res["eatApple"] == {"color": db_apple.color, "isEaten": True, "name": db_apple.name}
        db_apple.refresh_from_db()
        assert db_apple.is_eaten


class TestPermissionArgSchema(HasPermissionDirectiveInSchemaMixin, ArgTestCase):
    ...


class TestPermissionAsync(HasPermissionDirectiveInSchemaMixin, AsyncArgTestCase):
    ...
