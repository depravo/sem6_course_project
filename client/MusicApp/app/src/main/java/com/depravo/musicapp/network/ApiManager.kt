package com.depravo.musicapp.network

import com.depravo.musicapp.data.*
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ApiManager {
    fun signIn(login_cred: LoginCredentials, onResult: (LoginResponse?) -> Unit) {
        val retrofit = ServiceBuilder.buildService(IConnectAPI::class.java)
        retrofit.signIn(login_cred).enqueue(
            object : Callback<LoginResponse> {
                override fun onResponse(
                    call: Call<LoginResponse>,
                    response: Response<LoginResponse>
                ) {
                    var result = response.body()
                    onResult(result)
                }

                override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                    onResult(null)
                }
            }
        )
    }

    fun register(login_cred: LoginCredentials, onResult: (LoginResponse?) -> Unit) {
        val retrofit = ServiceBuilder.buildService(IConnectAPI::class.java)
        retrofit.register(login_cred).enqueue(
            object : Callback<LoginResponse> {
                override fun onResponse(
                    call: Call<LoginResponse>,
                    response: Response<LoginResponse>
                ) {
                    var result = response.body()
                    onResult(result)
                }

                override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                    onResult(null)
                }
            }
        )
    }

    fun getPlaylist(user_id: Int, onResult: (List<Song>?) -> Unit) {
        val retrofit = ServiceBuilder.buildService(IConnectAPI::class.java)
        retrofit.getPlaylist(user_id).enqueue(
            object : Callback<List<Song>> {
                override fun onResponse(
                    call: Call<List<Song>>,
                    response: Response<List<Song>>
                ) {
                    var result = response.body()
                    onResult(result)
                }

                override fun onFailure(call: Call<List<Song>>, t: Throwable) {
                    onResult(null)
                }
            }
        )
    }


    fun getRecommendations(user_id: Int, onResult: (List<Song>?) -> Unit) {
        val retrofit = ServiceBuilder.buildService(IConnectAPI::class.java)
        retrofit.getRecommendations(user_id).enqueue(
            object : Callback<List<Song>> {
                override fun onResponse(
                    call: Call<List<Song>>,
                    response: Response<List<Song>>
                ) {
                    var result = response.body()
                    onResult(result)
                }

                override fun onFailure(call: Call<List<Song>>, t: Throwable) {
                    onResult(null)
                }
            }
        )
    }

    fun addSongToPlaylist(credentials: AddingSongCredentials, onResult: (AddingSongResponse?) -> Unit) {
        val retrofit = ServiceBuilder.buildService(IConnectAPI::class.java)
        retrofit.addSongToPlaylist(credentials).enqueue(
            object : Callback<AddingSongResponse> {
                override fun onResponse(
                    call: Call<AddingSongResponse>,
                    response: Response<AddingSongResponse>
                ) {
                    var result = response.body()
                    onResult(result)
                }

                override fun onFailure(call: Call<AddingSongResponse>, t: Throwable) {
                    onResult(null)
                }
            }
        )
    }

    fun getSongsByName(substring: String, onResult: (List<Song>?) -> Unit) {
        val retrofit = ServiceBuilder.buildService(IConnectAPI::class.java)
        retrofit.getSongsByName(substring).enqueue(
            object : Callback<List<Song>> {
                override fun onResponse(
                    call: Call<List<Song>>,
                    response: Response<List<Song>>
                ) {
                    var result = response.body()
                    onResult(result)
                }

                override fun onFailure(call: Call<List<Song>>, t: Throwable) {
                     onResult(null)
                }
            }
        )
    }
}