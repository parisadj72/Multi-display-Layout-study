using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;

public class SelectionTask : MonoBehaviour
{
    private List<View> views = new List<View>();
    private List<int> windowsOn = new List<int>();

    private List<RawImage> rawImages = new List<RawImage>();

    private int numberOfWindows;
    private int windowNumberOn;
    public int selections = 5;

    private Boolean taskDone;

    public Boolean TaskDone
    {
        get { return taskDone; }
        set { taskDone = value; }
    }

    private void Awake()
    {
        InitializeLayout();
    }

    private void Start()
    {
        ExperimentSetup();
        GetRawImageList();
        StartCoroutine(Task1());
    }

    private void InitializeLayout()
    {
        Transform[] childTransforms = GetComponentsInChildren<Transform>();

        foreach (Transform childTransform in childTransforms)
        {
            View view = childTransform.GetComponent<View>();

            if (view != null)
            {
                views.Add(view);
            }
        }
        numberOfWindows = views.Count;
        //print(numberOfWindows);
        TaskDone = false;

    }

    private void GetRawImageList()
    {
        //string path = "Assets/Resources/Icons/";
        //string[] images = Directory.GetFiles(path, "*.png", SearchOption.TopDirectoryOnly);
        //foreach (string image in images)
        //{
        //    print(image);
        //}

        //    RawImage icon = AssetDatabase.LoadAssetAtPath(image, typeof(Texture2D)) as RawImage;
        //    print(icon.mainTexture);
        //    if (icon != null)
        //    {
        //        rawImages.Add(icon as RawImage);
        //        print("image added to list");
        //    }
        //}

        //foreach (RawImage rI in rawImages)
        //{
        //    print(rI.mainTexture.name);
        //}
        UnityEngine.Object[] textures;

        textures = Resources.LoadAll("ViewIcons", typeof(Texture2D));
        foreach (var t in textures)
        {
            Texture2D texture2D = t as Texture2D;
            print(texture2D.name);
            //rawImages.Add(texture2D);
            //Texture2D texture2D = t as Texture2D;
            //RawImage converted = 
            //converted.texture = texture2D;
            //rawImages.Add(converted);
        }

        foreach (RawImage t in rawImages)
        {
            print(t);
        }
        //    foreach (View view in views)
        //{
        //    view.RawIcon.texture = texture;
        //}
    }

    // This method is for task 1
    // It is meant to turn on one view at a time
    IEnumerator RandomWindowOn()
    {
        for (int i = selections; i > 0; i--)
        {
            windowNumberOn = UnityEngine.Random.Range(0, numberOfWindows);
            //print("Number was: " + turnedOnWindow);

            views[windowNumberOn].TurnOn(true);
            //print("Window on is: " + (turnedOnWindow + 1));

            yield return new WaitUntil(() => !views[windowNumberOn].IsOn);
        }
        TaskDone = true;
    }

    //IEnumerator RandomWindowsOn(int onToBe)
    //{
    //    for (int i = selections; i > 0; i--)
    //    {
    //        windowsOn = RandomGenerator.randomizeList(numberOfWindows);

    //        for (int j = 0; j < windowsOn.Count; j++)
    //        {
    //            views[j].TurnOn(true);

    //        }
    //        //print("Number was: " + turnedOnWindow);

    //        //print("Window on is: " + (turnedOnWindow + 1));

    //        yield return new WaitUntil(() => areViewsOn());
    //    }
    //    TaskDone = true;
    //}

    IEnumerator Task1()
    {
        //DisableDrag();
        StartCoroutine(RandomWindowOn());
        yield return new WaitUntil(() => TaskDone);
        print("Task1 is finished");
    }

    private void TraverseList(List<View> list)
    {
        foreach (View view in list)
        {
            print(view.name);
        }
    }

    public void DisableDrag()
    {
        foreach (View view in views)
        {
            view.GetComponent<XRGrabInteractable>().enabled = false;
            view.GetComponent<BoxCollider>().enabled = false;
        }
    }

    private void ExperimentSetup()
    {
        Experiment1 parent = GetComponentInParent<Experiment1>();

        switch (parent.experiment)
        {
            case Experiment1.Experiment.Exp1:
                print("Exp1 selected");
                DisableDrag();
                break;
            case Experiment1.Experiment.Exp2:
                print("Exp2 selected");
                DisableDrag();
                break;
            case Experiment1.Experiment.Exp3:
                print("Exp3 selected");
                break;
        }
    }
}
