package com.depravo.musicapp.data

data class LoginResponse(val success: Boolean, val message: String, val userId: Int)

data class LoginCredentials(val username: String, val password: String)

data class Song(val name: String, val artist: String, val logoResource: String)

data class AddingSongCredentials(val userId: Int, val songName: String)

data class AddingSongResponse(val success: Boolean, val message: String)
