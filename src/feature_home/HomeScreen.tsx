import React, {useEffect} from 'react'
import {Text, View} from "react-native";
import {ApiResponse} from "../shared/domain/ApiResponse";
import {fetchTopArticles} from "../shared/api/RecentArticlesDataSource";

export const HomeScreen = () => {

    useEffect(() => {
        getTopHeadlines().then(topHeadlinesData => {
            if (topHeadlinesData && topHeadlinesData.articles) {

                console.log("The content we received from GNews:\n\n");
                for (const article of topHeadlinesData.articles) {
                    console.log(article.title, "\n");
                }

            }
        });
    }, []);

    const getTopHeadlines = async () => {
        let data: ApiResponse | null;
        data = await fetchTopArticles();
        return data
    }


    return (
        <View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
            <Text>This is the HomeScreen</Text>
        </View>
    )
}
