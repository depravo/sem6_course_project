package com.depravo.musicapp.ui

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Toast
import com.depravo.musicapp.databinding.ActivityLoginBinding
import com.depravo.musicapp.network.ApiManager
import com.depravo.musicapp.data.*

class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private val apiService = ApiManager()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val login = binding.login
        val password = binding.password
        val signInBtn = binding.signIn
        val registerBtn = binding.register

        signInBtn.setOnClickListener {
            if (!login.text.isEmpty() && !password.text.isEmpty()) {
                val login_cred = LoginCredentials(login.text.toString(), password.text.toString())
                apiService.signIn(login_cred) {
                    if (it?.success == true) {
                        val infoIntent = Intent(this@LoginActivity, MainActivity::class.java)
                        infoIntent.putExtra("user_id", it?.userId.toString())
                        Toast.makeText(
                            applicationContext,
                            it?.message,
                            Toast.LENGTH_SHORT
                        ).show()
                        startActivity(infoIntent)
                    }
                }
            } else {
                Toast.makeText(
                    applicationContext,
                    "Enter login or password",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
        registerBtn.setOnClickListener {
            if (!login.text.isEmpty() && !password.text.isEmpty()) {
                val login_cred = LoginCredentials(login.text.toString(), password.text.toString())
                apiService.register(login_cred) {
                    if (it?.success == true) {
                        val infoIntent = Intent(this@LoginActivity, MainActivity::class.java)
                        infoIntent.putExtra("user_id", it?.userId)
                        Toast.makeText(
                            applicationContext,
                            it?.message,
                            Toast.LENGTH_SHORT
                        ).show()
                        startActivity(infoIntent)
                    }
                }
            } else {
                Toast.makeText(
                    applicationContext,
                    "Enter login and password",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

}