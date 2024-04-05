package com.depravo.musicapp.network

import com.depravo.musicapp.data.*
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

interface IConnectAPI {
    @POST("/signIn")
    fun signIn(@Body credentials: LoginCredentials): Call<LoginResponse>

    @POST("/register")
    fun register(@Body credentials: LoginCredentials): Call<LoginResponse>

    @POST("/playlist")
    fun getPlaylist(@Body user_id: Int) : Call<List<Song>>

    @POST("/recommendations")
    fun getRecommendations(@Body user_id: Int) : Call<List<Song>>

    @POST("/addSong")
    fun addSongToPlaylist(@Body credentials: AddingSongCredentials) : Call<AddingSongResponse>

    @POST("/getSongsByName")
    fun getSongsByName(@Body substring: String) : Call<List<Song>>
}