using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;

public class SelectionTask : MonoBehaviour
{
    private List<View> views = new List<View>();

    private List<Texture2D> textures = new List<Texture2D>();
    private List<int> randomIcons;

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
        InitializeIconList();
        RandomizeIcons();
        ExperimentSetup();
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

    private void InitializeIconList()
    {
        UnityEngine.Object[] loadedIcons;

        loadedIcons = Resources.LoadAll("ViewIcons", typeof(Texture2D));

        foreach (var icon in loadedIcons)
        {
            Texture2D texture2D = icon as Texture2D;
            textures.Add(texture2D);
        }

        //foreach (Texture2D icon in textures)
        //{
        //    print(icon.name);
        //}
    }

    private void RandomizeIcons()
    {
        randomIcons = RandomGenerator.randomizeList(textures.Count);

        for (int i = 0; i < views.Count; i++)
        {
            views[i].RawIcon.texture = textures[randomIcons[i]];
        }
    }

    // This method is for task 1
    // It is meant to turn on one view at a time
    IEnumerator RandomWindowOn()
    {
        for (int i = selections; i > 0; i--)
        {
            windowNumberOn = UnityEngine.Random.Range(0, numberOfWindows);
            //print("Number was: " + turnedOnWindow);

            views[windowNumberOn].TurnOn(true, true);
            //print("Window on is: " + (turnedOnWindow + 1));

            yield return new WaitUntil(() => !views[windowNumberOn].IsOn);
        }
        TaskDone = true;
    }

    IEnumerator RandomWindowsOn()
    {
        List<int> windowsOn;

        switch (numberOfWindows)
        {
            case 3:
                selections = 2;
                //print("3-view layout");
                windowsOn = RandomGenerator.randomizeList(numberOfWindows);

                for (int i = 0; i < 2; i++)
                {
                    views[windowsOn[i]].TurnOn(true, false);
                }

                yield return new WaitForSeconds(5);

                for (int i = 0; i < 2; i++)
                {
                    views[windowsOn[i]].TurnOn(false, true);
                }

                for (int i = 0; i < 2; i++)
                {
                    yield return new WaitUntil(() => views[windowsOn[i]].IsOn);
                }

                TaskDone = true;
                break;
            case 6:
                selections = 3;
                //print("6-view layout");
                windowsOn = RandomGenerator.randomizeList(numberOfWindows);
                TraverseList(windowsOn);

                for (int i = 0; i < 3; i++)
                {
                    views[windowsOn[i]].TurnOn(true, false);
                }

                yield return new WaitForSeconds(5);

                for (int i = 0; i < 3; i++)
                {
                    views[windowsOn[i]].TurnOn(false, true);
                }

                for (int i = 0; i < 3; i++)
                {
                    yield return new WaitUntil(() => views[windowsOn[i]].IsOn);
                }

                TaskDone = true;
                break;
            case 12:
                selections = 5;
                //print("12-view layout");
                windowsOn = RandomGenerator.randomizeList(numberOfWindows);
                TraverseList(windowsOn);

                for (int i = 0; i < 5; i++)
                {
                    views[windowsOn[i]].TurnOn(true, false);
                }

                yield return new WaitForSeconds(5);

                for (int i = 0; i < 5; i++)
                {
                    views[windowsOn[i]].TurnOn(false, true);
                }

                for (int i = 0; i < 5; i++)
                {
                    yield return new WaitUntil(() => views[windowsOn[i]].IsOn);
                }
                TaskDone = true;
                break;
        }

        yield return new WaitForSeconds(1);

        //List<int> windows = RandomGenerator.randomizeList(numberOfWindows);
        //for (int i = 0; i < numberOfWindows; i++)
        //{
        //    views[windows[i]].TurnOn(true);
        //    yield return new WaitForSeconds(5);
        //    views[windows[i]].TurnOff();
        //}

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

    IEnumerator Task2()
    {
        StartCoroutine(RandomWindowsOn());
        yield return new WaitUntil(() => TaskDone);
        print("Task2 is finished");
    }

    private void TraverseList(List<View> list)
    {
        foreach (View view in list)
        {
            print(view.name);
        }
    }

    private void TraverseList(List<int> list)
    {
        foreach (int view in list)
        {
            print(view);
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
                StartCoroutine(Task1());
                break;
            case Experiment1.Experiment.Exp2:
                print("Exp2 selected");
                DisableDrag();
                StartCoroutine(Task2());
                break;
            case Experiment1.Experiment.Exp3:
                print("Exp3 selected");
                break;
        }
    }
}
