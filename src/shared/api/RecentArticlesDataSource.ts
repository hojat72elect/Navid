import {API_BASE_URL as baseUrl} from "./Constants";
import {ApiKey} from "./ApiKeySecret";
import {ApiGNewsService} from "./ApiGNewsService";


const topArticlesEndpoint = `${baseUrl}/top-headlines?apikey=${ApiKey}`;

/**
 * For getting all the top news articles of Canada.
 * We'll show them in the main page.
 */
export const fetchTopArticles = () => {
    return ApiGNewsService(topArticlesEndpoint, {category: "general", lang: "en", country: "ca", max: 5});
}