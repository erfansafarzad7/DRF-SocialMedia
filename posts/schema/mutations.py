from posts.models import Post, Tag, StatusChoices
from posts.schema.types import PostType

import graphene


class CreatePost(graphene.Mutation):
    """
    Mutation to create a new post.

    Arguments:
        image (str): The URL or path of the image for the post.
        caption (str): The caption for the post.
        author_id (int): The ID of the author who is creating the post.

    Returns:
        PostType: The created post object.
    """

    class Arguments:
        image = graphene.String(required=True)
        caption = graphene.String(required=True)
        author_id = graphene.Int(required=True)

    post = graphene.Field(PostType)

    def mutate(self, info, image, caption, author_id):
        post = Post.objects.create(
            image=image,
            caption=caption,
            author_id=author_id,
        )
        return CreatePost(post=post)


class UpdatePost(graphene.Mutation):
    """
    Mutation to update an existing post.

    Arguments:
        id (int): The ID of the post to be updated.
        caption (str): The new caption for the post (optional).

    Returns:
        PostType: The updated post object.
    """

    class Arguments:
        id = graphene.Int(required=True)
        caption = graphene.String()

    post = graphene.Field(PostType)

    def mutate(self, info, id, caption=None):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            raise Exception("Post not found")

        if caption:
            post.caption = caption

        post.save()
        return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    """
    Mutation to delete a post.

    Arguments:
        id (int): The ID of the post to be deleted.

    Returns:
        success (bool): Whether the deletion was successful.
    """

    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            post = Post.objects.get(id=id)
            post.delete()
            return DeletePost(success=True)
        except Post.DoesNotExist:
            return DeletePost(success=False)


class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
