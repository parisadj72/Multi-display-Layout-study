using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;

public class TaskManagement : MonoBehaviour
{
    private List<View> views = new List<View>();
    private List<LayoutSocket> sockets = new List<LayoutSocket>();
    private PuzzleLayout puzzleLayout;
    private Experiments parent;

    private List<Texture2D> textures = new List<Texture2D>();
    private List<int> randomIcons;

    private List<int> viewOrder;

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
        viewOrder = RandomGenerator.randomizeList(numberOfWindows);
        randomIcons = RandomGenerator.randomizeList(numberOfWindows);
        print("Icons: " + randomIcons.Count);
        RandomizeIcons();

        ExperimentSetup();
    }

    private void InitializeLayout()
    {
        parent = GetComponentInParent<Experiments>();
        puzzleLayout = GetComponentInChildren<PuzzleLayout>(true);

        Transform[] childTransforms = GetComponentsInChildren<Transform>();

        foreach (Transform childTransform in childTransforms)
        {
            View view = childTransform.GetComponent<View>();
            LayoutSocket socket = childTransform.GetComponent<LayoutSocket>();

            if (view != null && view.gameObject.tag.Equals("View"))
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
        print("Layout windows: " + numberOfWindows);
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
        for (int i = 0; i < views.Count; i++)
        {
            views[i].RawIcon.texture = textures[randomIcons[i]];
        }
    }

    private void CopyLayout()
    {
        puzzleLayout.CopyFields(textures, randomIcons, viewOrder);
    }

    private bool IsExp3()
    {
        return (parent.experiment == Experiments.Experiment.Exp3);
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
        selections = (numberOfWindows / 3) + 1;

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].TurnOn(true, false);

        yield return new WaitForSeconds(5);

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].TurnOn(false, true);


        for (int i = 0; i < selections; i++)
        {
            yield return new WaitUntil(() => checkAllOnDisableOns(views, viewOrder));
        }

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].DisableInteraction();

        TaskDone = true;

        yield return new WaitForSeconds(1);
    }

    private bool checkAllOnDisableOns(List<View> views, List<int> viewOrder)
    {
        for (int i = 0; i < selections; i++)
            if (views[viewOrder[i]].IsOn)
                views[viewOrder[i]].DisableInteraction();
        for (int i = 0; i < selections; i++)
        {
            if (views[viewOrder[i]].IsOn)
                continue;
            else
                return false;
        }
        return true;
    }

    IEnumerator KeepRandomOn()
    {
        selections = (numberOfWindows / 3) + 1;

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].TurnOn(true, false);

        yield return new WaitForSeconds(5);

       

        //TaskDone = true;

        yield return new WaitForSeconds(1);
    }

    IEnumerator CountWindowsOn()
    {
        int onCount = 0;

        foreach (View view in views)
        {
            if (view.IsOn)
            {
                onCount++;
                yield return new WaitUntil(() => onCount == selections);
            }
        }
    }

    IEnumerator Task1()
    {
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

    IEnumerator Task3()
    {
        CopyLayout();
        KeepRandomOn();
        // Call coroutine here and set task done
        yield return new WaitUntil(() => TaskDone);
        print("Task3 is finished");
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

    private void ExperimentSetup()
    {

        if (parent == null)
        {
            print("parent is null");
        }

        switch (parent.experiment)
        {
            case Experiments.Experiment.Exp1:
                print("Exp1 selected");
                DisableDrag();
                StartCoroutine(Task1());
                break;
            case Experiments.Experiment.Exp2:
                print("Exp2 selected");
                DisableDrag();
                StartCoroutine(Task2());
                break;
            case Experiments.Experiment.Exp3:
                print("Exp3 selected");
                puzzleLayout.gameObject.SetActive(true);
                // StartCoroutine() or method to copy and randomize puzzle layout
                StartCoroutine(Task3());
                break;

            default:
                print("got copied?");
                break;
        }
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
}
