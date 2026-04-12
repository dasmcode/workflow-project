import strawberry
from strawberry.fastapi import GraphQLRouter
from graphql_app.schemas.file_schema import FileQuery, FileMutation
from graphql_app.schemas.job_schema import JobQuery, JobMutation, JobSubscription
from graphql_app.context.graphql_context import get_context

try:
    from strawberry.subscriptions import (
        GRAPHQL_TRANSPORT_WS_PROTOCOL,
        GRAPHQL_WS_PROTOCOL,
    )
except ImportError:
    from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL

    GRAPHQL_WS_PROTOCOL = "graphql-ws"


@strawberry.type
class Query(FileQuery, JobQuery):
    pass


@strawberry.type
class Mutation(FileMutation, JobMutation):
    pass


@strawberry.type
class Subscription(JobSubscription):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    multipart_uploads_enabled=True,
    graphql_ide="apollo-sandbox",
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL],
    prefix="/api/v1/workflow",
)
