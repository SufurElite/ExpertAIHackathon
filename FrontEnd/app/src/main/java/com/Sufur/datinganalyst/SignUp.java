package com.Sufur.datinganalyst;

import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.text.method.PasswordTransformationMethod;
import android.text.method.HideReturnsTransformationMethod;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

public class SignUp extends AppCompatActivity {
    private Button signUp;

    private CheckBox passwordOneVisibility;
    private CheckBox passwordTwoVisibility;
    private EditText emailText;
    private EditText passwordOne;
    private EditText passwordTwo;
    private FirebaseAuth mAuth;

    // Email Regex
    public static final Pattern VALID_EMAIL_ADDRESS_REGEX =
            Pattern.compile("^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,6}$", Pattern.CASE_INSENSITIVE);
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.sign_up);
        mAuth = FirebaseAuth.getInstance();
        Common.currentUser = mAuth.getCurrentUser();
        if(Common.currentUser != null){
            startActivity(new Intent(SignUp.this, ChatActivity.class));
            finish();
        }
        initializeView();
    }

    public boolean validateEmail(String email){
        // https://stackoverflow.com/questions/8204680/java-regex-email
        Matcher matcher = VALID_EMAIL_ADDRESS_REGEX.matcher(email);
        return matcher.find();
    }

    private void createAccount(String email, String password){
        mAuth.createUserWithEmailAndPassword(email, password).addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
            @Override
            public void onComplete(@NonNull Task<AuthResult> task) {
                if(task.isSuccessful()){
                    // Sign in success, update UI with the signed-in user's information
                    Log.d("Sign-Up", "createUserWithEmail:success");
                    Common.currentUser = mAuth.getCurrentUser();
                    startActivity(new Intent(SignUp.this, ChatActivity.class));
                    finish();
                } else {
                    // If sign in fails, display a message to the user.
                    Log.w("Sign-Up", "signInWithEmail:failure", task.getException());
                    Toast.makeText(SignUp.this, "Authentication failed.",
                            Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void initializeView() {

        passwordOne = findViewById(R.id.password);
        passwordTwo = findViewById(R.id.password_2);

        emailText = findViewById(R.id.email);

        signUp = findViewById(R.id.signUpButton);

        passwordOneVisibility = findViewById(R.id.checkBox);
        passwordOneVisibility.setOnClickListener(new View.OnClickListener() {
           @Override
           public void onClick(View view){
               if (((CheckBox)view).isChecked()){
                   passwordOne.setTransformationMethod(HideReturnsTransformationMethod.getInstance());
               } else {
                   passwordOne.setTransformationMethod(PasswordTransformationMethod.getInstance());
               }
           }
        });

        passwordTwoVisibility = findViewById(R.id.checkBox2);
        passwordTwoVisibility.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view){
                if (((CheckBox)view).isChecked()){
                    passwordTwo.setTransformationMethod(HideReturnsTransformationMethod.getInstance());
                } else {
                    passwordTwo.setTransformationMethod(PasswordTransformationMethod.getInstance());
                }
            }
        });

        signUp.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (!passwordOne.getText().toString().equals(passwordTwo.getText().toString()) || !(passwordOne.getText().toString().length()>=5)) {
                    new AlertDialog.Builder(SignUp.this)
                            .setTitle("Non-Equal Passwords")
                            .setMessage("Ensure that you've provided the same passwords of at least length 5.")
                            // Specifying a listener allows you to take an action before dismissing the dialog.
                            // The dialog is automatically dismissed when a dialog button is clicked.
                            .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface dialog, int which) {
                                    // Continue with delete operation
                                }
                            })
                            .setIcon(android.R.drawable.ic_dialog_alert)
                            .show();
                } else if(!validateEmail(emailText.getText().toString())){
                    new AlertDialog.Builder(SignUp.this)
                            .setTitle("Email")
                            .setMessage("Please enter a valid email")
                            // Specifying a listener allows you to take an action before dismissing the dialog.
                            // The dialog is automatically dismissed when a dialog button is clicked.
                            .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface dialog, int which) {
                                    // Continue with delete operation
                                }
                            })
                            .setIcon(android.R.drawable.ic_dialog_alert)
                            .show();
                } else {
                    createAccount(emailText.getText().toString(), passwordOne.getText().toString());
                }
            }
        });
    }
}
