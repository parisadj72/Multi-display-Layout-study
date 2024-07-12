using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

public class LayoutCopy : MonoBehaviour
{
    private List<View> views = new List<View>();
    private List<LayoutSocket> sockets = new List<LayoutSocket>();

    private List<Texture2D> textures = new List<Texture2D>();
    private List<int> randomIcons;

    List<int> windowsOn;

    private int numberOfWindows;
    private int windowNumberOn;
    public int selections = 5;

    private Boolean taskDone;

    public Boolean TaskDone
    {
        get { return taskDone; }
        set { taskDone = value; }
    }

    public List<View> Views
    {
        get { return views; }
        set { views = value; }
    }

    public List<Texture2D> Textures { get => textures; set => textures = value; }
    public List<int> RandomIcons { get => randomIcons; set => randomIcons = value; }
    public int NumberOfWindows { get => numberOfWindows; set => numberOfWindows = value; }

    private void Awake()
    {
        InitializeLayout();
    }

    private void Start()
    {
        InitializeIconList();
        RandomizeIcons();
    }

    private void InitializeLayout()
    {
        Transform[] childTransforms = GetComponentsInChildren<Transform>();

        foreach (Transform childTransform in childTransforms)
        {
            View view = childTransform.GetComponent<View>();
            LayoutSocket socket = childTransform.GetComponent<LayoutSocket>();

            if (view != null)
            {
                views.Add(view);
            }

            if (socket != null)
            {
                sockets.Add(socket);
            }
        }
        numberOfWindows = views.Count;
        //print(sockets.Count);
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
    }

    private void RandomizeIcons()
    {
        randomIcons = RandomGenerator.randomizeList(textures.Count);

        for (int i = 0; i < views.Count; i++)
        {
            views[i].RawIcon.texture = textures[randomIcons[i]];
        }
    }

    //public SelectionTask CopyLayout(SelectionTask layout)
    //{
    //    SelectionTask copy = new SelectionTask();
    //    copy.Textures = layout.Textures;
    //    copy.
    //}

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

        foreach (LayoutSocket socket in sockets)
        {
            socket.gameObject.SetActive(false);
        }
    }
}
