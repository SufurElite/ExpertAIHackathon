package com.Sufur.datinganalyst;


import okhttp3.MultipartBody;
import okhttp3.ResponseBody;
import retrofit2.http.GET;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Path;
import retrofit2.http.Query;
import retrofit2.Call;

public interface ApiInterface {
    @GET("/users/{user}")
    Call<String> getApiResponse(@Path("user") String user);

    @GET("/getImageText/{path}")
    Call<String> postImage(@Path("path")String path);

    @GET("/potentialMessage/{path}/{msg}")
    Call<String> potentialMessage(@Path("path")String path, @Path("msg")String msg);
}
