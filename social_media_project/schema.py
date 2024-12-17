from posts.schema import queries, mutations
import graphene


schema = graphene.Schema(query=queries.Query, mutation=mutations.Mutation)
