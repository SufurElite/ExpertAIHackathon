package com.Sufur.datinganalyst;

import retrofit2.Retrofit;
import retrofit2.converter.scalars.ScalarsConverterFactory;

public class ApiClient {
    // Will point to the server, whether hosted on G-Cloud, Heroku, or just on the Desktop
    private static final String BASE_URL = "";
    private static Retrofit retrofit;
    public static Retrofit getApiClient(char c)
    {
        if(retrofit==null){
            if(c=='s') {
                retrofit = new Retrofit.Builder().baseUrl(BASE_URL).addConverterFactory(ScalarsConverterFactory.create()).build();
            } else {
                retrofit = new Retrofit.Builder().baseUrl(BASE_URL).build();
            }
        }
        return retrofit;
    }
}
