import {ApiArticle} from "./ApiArticle";

export type ApiResponse = {
  totalArticles: number;
  articles: ApiArticle[];
}