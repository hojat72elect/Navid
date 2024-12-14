import {ApiArticleSource} from "./ApiArticleSource";

export type ApiArticle = {
    title: string;
    description: string;
    content: string;
    url: string;
    image: string;
    publishedAt: string;
    source: ApiArticleSource;
}