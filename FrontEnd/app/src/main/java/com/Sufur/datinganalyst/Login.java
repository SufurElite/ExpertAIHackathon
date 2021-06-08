package com.Sufur.datinganalyst;

import android.content.Intent;
import android.os.Bundle;
import android.text.method.HideReturnsTransformationMethod;
import android.text.method.PasswordTransformationMethod;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

public class Login extends AppCompatActivity {

    private Button loginBtn;

    private CheckBox passwordVisibility;
    private EditText emailText;
    private EditText passwordText;
    private FirebaseAuth mAuth;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.login_page);
        mAuth = FirebaseAuth.getInstance();
        Common.currentUser = mAuth.getCurrentUser();
        if(Common.currentUser != null){
            startActivity(new Intent(Login.this, ChatActivity.class));
            finish();
        }
        initializeView();
    }

    private void signIn(String email, String password){
        mAuth.signInWithEmailAndPassword(email, password).addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
            @Override
            public void onComplete(@NonNull Task<AuthResult> task) {
                if (task.isSuccessful()){
                    // Successful login
                    Log.d("Login","signIn:success");
                    Common.currentUser = mAuth.getCurrentUser();
                    startActivity(new Intent(Login.this, ChatActivity.class));
                    finish();
                } else {
                    Log.d("Login", "signIn:Failure",task.getException());
                    Toast.makeText(Login.this, "Authentication failed.", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }
    private void initializeView(){
        passwordText = findViewById(R.id.password);

        emailText = findViewById(R.id.email);

        loginBtn = findViewById(R.id.loginButton);

        passwordVisibility = findViewById(R.id.checkBox);
        passwordVisibility.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view){
                if (((CheckBox)view).isChecked()){
                    passwordText.setTransformationMethod(HideReturnsTransformationMethod.getInstance());
                } else {
                    passwordText.setTransformationMethod(PasswordTransformationMethod.getInstance());
                }
            }
        });

        loginBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view){
                signIn(emailText.getText().toString(), passwordText.getText().toString());
            }
        });

    }
}
