import asyncio
from typing import AsyncGenerator, Union

import strawberry
import strawberry_django

from gqlauth.core.directives import HasPermission, IsVerified, TokenRequired
from gqlauth.core.field_ import field, subscription
from gqlauth.core.types_ import GQLAuthError
from gqlauth.user import arg_mutations
from gqlauth.user.arg_mutations import Captcha
from gqlauth.user.queries import UserQueries
from testproject.sample.models import Apple


@strawberry.type
class AuthMutation:
    verify_token = arg_mutations.VerifyToken.field
    update_account = arg_mutations.UpdateAccount.field
    archive_account = arg_mutations.ArchiveAccount.field
    delete_account = arg_mutations.DeleteAccount.field
    password_change = arg_mutations.PasswordChange.field

    @field(directives=[HasPermission(permissions=["sample.can_eat"])])
    def eat_apple(self, apple_id: int) -> Union["AppleType", GQLAuthError]:
        apple = Apple.objects.get(id=apple_id)
        apple.is_eaten = True
        apple.save()
        return apple


@strawberry.type
class Mutation:
    @field(directives=[TokenRequired()])
    def auth_entry(self) -> Union[AuthMutation, GQLAuthError]:
        return AuthMutation()

    captcha = Captcha.field
    token_auth = arg_mutations.ObtainJSONWebToken.field
    register = arg_mutations.Register.field
    verify_account = arg_mutations.VerifyAccount.field
    resend_activation_email = arg_mutations.ResendActivationEmail.field
    send_password_reset_email = arg_mutations.SendPasswordResetEmail.field
    password_reset = arg_mutations.PasswordReset.field
    password_set = arg_mutations.PasswordSet.field
    refresh_token = arg_mutations.RefreshToken.field
    revoke_token = arg_mutations.RevokeToken.field


@strawberry_django.type(model=Apple)
class AppleType:
    color: strawberry.auto
    name: strawberry.auto
    is_eaten: strawberry.auto


@strawberry.type
class AuthQueries(UserQueries):
    @field(
        directives=[
            IsVerified(),
        ]
    )
    def apple(self) -> Union[GQLAuthError, AppleType]:
        return Apple.objects.latest("pk")


@strawberry.type
class Query:
    @field(
        directives=[
            TokenRequired(),
        ]
    )
    def auth_entry(self) -> Union[GQLAuthError, AuthQueries]:
        return AuthQueries()

    @field(directives=[TokenRequired(), IsVerified()])
    @staticmethod
    def batched_field() -> Union["AppleType", GQLAuthError]:
        return Apple.objects.latest("pk")


@strawberry.type
class Integer:
    """
    graphql unions cannot contain scalars.
    """

    node: int


@strawberry.type
class Subscription:
    @subscription(
        directives=[
            TokenRequired(),
        ],
        is_subscription=True,
    )
    async def count(self, target: int = 10) -> AsyncGenerator[Union[Integer, GQLAuthError], None]:
        for i in range(target):
            yield Integer(node=i)
            await asyncio.sleep(0.5)


arg_schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
