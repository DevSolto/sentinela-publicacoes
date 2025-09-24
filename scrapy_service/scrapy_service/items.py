"""Scrapy item definitions used across spiders."""

import scrapy


class ProfileItem(scrapy.Item):
    entity = scrapy.Field(default="profile")
    profile_id = scrapy.Field()
    display_name = scrapy.Field()
    source = scrapy.Field()
    metadata = scrapy.Field()


class PostItem(scrapy.Item):
    entity = scrapy.Field(default="post")
    post_id = scrapy.Field()
    profile_id = scrapy.Field()
    body = scrapy.Field()
    created_at = scrapy.Field()
    stats = scrapy.Field()
    source = scrapy.Field()
    comments_endpoint = scrapy.Field()
    comments_payload = scrapy.Field()


class CommentItem(scrapy.Item):
    entity = scrapy.Field(default="comment")
    comment_id = scrapy.Field()
    post_id = scrapy.Field()
    profile_id = scrapy.Field()
    body = scrapy.Field()
    author = scrapy.Field()
    created_at = scrapy.Field()
    source = scrapy.Field()


__all__ = ["ProfileItem", "PostItem", "CommentItem"]

