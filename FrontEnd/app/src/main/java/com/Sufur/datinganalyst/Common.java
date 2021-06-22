package com.Sufur.datinganalyst;

import android.graphics.Bitmap;

import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.storage.FirebaseStorage;

public class Common {
    // the string will be saved in here when min/max is pressed
    public static String currentInput = "";
    // string stored here when save is pressed
    public static String savedInput = "";
    public static int inquisitiveness;
    public static int interestingness;
    public static int ghostedness;
    public static String bitmapName = "";
    public static FirebaseUser currentUser;
    public static FirebaseStorage db;
    public static Bitmap bitmap;
    public static boolean analysis = false;
    public static boolean floatingRunning = false;
    public static int displayWidth;
    public static int displayHeight;

}
