import axios from "axios";

/**
 * The parameters that user provides for this service should conform
 * to this type.
 */
export type SearchParams = {
    category: string;
    lang: string;
    country: string;
    max: number;
};

/**
 * The API call you make should conform to this.
 */
type ApiCallOptions = {
    method: string;
    url: string;
    params: SearchParams | null;
};

/**
 * This interface is the connecting point to the GNews service.
 */
export const ApiGNewsService = async (endpoint: string, params?: SearchParams) => {
    const options: ApiCallOptions = {
        method: 'GET',
        url: endpoint,
        params: params ? params : null,
    };

    try {
        const response = await axios.request(options);
        return response.data;
    } catch (error) {
        console.error('error: ', error);
        return {};
    }
}
