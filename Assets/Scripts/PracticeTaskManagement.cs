using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.UI;
using TMPro;

public class PracticeTaskManagement : MonoBehaviour
{
    private List<PracticeView> views = new List<PracticeView>();
    private List<LayoutSocket> sockets = new List<LayoutSocket>();
    private PracticePuzzleLayout puzzleLayout;
    private List<PracticeView> puzzleViews = new List<PracticeView>();
    private PracticeExperiments parent;

    private List<Texture2D> textures = new List<Texture2D>();
    private List<int> randomIcons;

    private List<int> viewOrder;

    private int numberOfWindows;
    private int windowNumberOn;
    public int selections = 5;
    public int task1Selections = 5;
    private int selectedViewsCounter = 0;

    private Boolean taskDone;

    public Boolean TaskDone
    {
        get { return taskDone; }
        set { taskDone = value; }
    }

    public List<PracticeView> Views
    {
        get { return views; }
        set { views = value; }
    }

    public List<Texture2D> Textures { get => textures; set => textures = value; }
    public List<int> RandomIcons { get => randomIcons; set => randomIcons = value; }
    public int NumberOfWindows { get => numberOfWindows; set => numberOfWindows = value; }
    public int SelectedViewsCounter { get => selectedViewsCounter; set => selectedViewsCounter = value; }

    private void Awake()
    {
        InitializeLayout();
    }

    private void Start()
    {
        InitializeIconList();
        viewOrder = RandomGenerator.randomizeList(numberOfWindows);
        randomIcons = RandomGenerator.randomizeList(numberOfWindows);
        RandomizeIcons();

        ExperimentSetup();
    }

    private void InitializeLayout()
    {
        parent = GetComponentInParent<PracticeExperiments>();
        puzzleLayout = GetComponentInChildren<PracticePuzzleLayout>(true);

        Transform[] childTransforms = GetComponentsInChildren<Transform>();

        foreach (Transform childTransform in childTransforms)
        {
            PracticeView view = childTransform.GetComponent<PracticeView>();
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

        selections = (numberOfWindows / 3) + 1;

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

    // This method is for task 1
    // It is meant to turn on one view at a time
    IEnumerator RandomWindowOn()
    {
        GameObject userPrompt = GameObject.FindGameObjectWithTag("PromptText");
        userPrompt.GetComponent<TextMeshPro>().text = "";

        for (int i = task1Selections; i > 0; i--)
        {
            windowNumberOn = UnityEngine.Random.Range(0, numberOfWindows);
            //print("Number was: " + windowNumberOn);

            views[windowNumberOn].TurnOn(true, true);
            //print("Window on is: " + (turnedOnWindow + 1));

            yield return new WaitUntil(() => !views[windowNumberOn].IsOn);
        }

        // show a hint to user that all views has been selected
        userPrompt.GetComponent<TextMeshPro>().text = "Well Done!";

        TaskDone = true;
    }

    IEnumerator RandomWindowsOn()
    {
        GameObject userPrompt = GameObject.FindGameObjectWithTag("PromptText");
        userPrompt.GetComponent<TextMeshPro>().text = "";

        GameObject left = GameObject.FindGameObjectWithTag("LeftRay");
        GameObject right = GameObject.FindGameObjectWithTag("RightRay");

        XRInteractorLineVisual leftRay = left.GetComponent<XRInteractorLineVisual>();
        XRInteractorLineVisual rightRay = right.GetComponent<XRInteractorLineVisual>();

        leftRay.enabled = false;
        rightRay.enabled = false;

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].TurnOn(true, false);

        yield return new WaitForSeconds(5);

        leftRay.enabled = true;
        rightRay.enabled = true;

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].TurnOn(false, true);


        for (int i = 0; i < selections; i++)
        {
            yield return new WaitUntil(() => checkAllOnDisableOns(views, viewOrder));
        }

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].DisableInteraction();

        // show a hint to user that all views has been selected
        userPrompt.GetComponent<TextMeshPro>().text = "Well Done!";

        TaskDone = true;

        yield return new WaitForSeconds(1);
    }

    private bool checkAllOnDisableOns(List<PracticeView> views, List<int> viewOrder)
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

    IEnumerator PuzzleTaskSwap()
    {
        selections = (numberOfWindows / 3) + 1;

        for (int i = 0; i < selections; i++)
        {
            puzzleViews.Add(views[viewOrder[i]]);
            puzzleViews[i].TurnOn(true, true);
        }

        for (int i = 0; i < views.Count; i++)
        {
            if (!views[i].IsOn)
            {
                DisableDrag(views[i], sockets[i]);
                views[i].GetComponent<TrackedDeviceGraphicRaycaster>().enabled = false;
            }
        }

        //yield return new WaitUntil(() => TwoViewsSelected());

        yield return new WaitUntil(() => CpompareIcons(puzzleLayout));

        TaskDone = true;
    }

    private bool CpompareIcons(PracticePuzzleLayout puzzleLayout)
    {
        for (int i = 0; i < puzzleViews.Count; i++)
        {
            if (!puzzleViews[i].IsOn || (puzzleViews[i].RawIcon.texture.name.Equals(puzzleLayout.TexlistOns[i].name)))
            {
                continue;
            }
            else return false;
        }

        for (int i = 0; i < puzzleViews.Count; i++)
        {
            puzzleViews[i].DisableInteraction();
        }

        return true;
    }
    private void SwapTwoViewsSelected()
    {
        if (selectedViewsCounter == 2)
        {
            List<Texture> images = new List<Texture>();
            List<int> index = new List<int>();

            for (int i = 0; i < puzzleViews.Count; i++)
            {
                if (puzzleViews[i].IsSelected)
                {
                    images.Add(puzzleViews[i].RawIcon.texture);
                    index.Add(i);
                    puzzleViews[i].IsSelected = false;
                }
            }
            // now swap..
            puzzleViews[index[0]].RawIcon.texture = images[1];
            puzzleViews[index[1]].RawIcon.texture = images[0];
            puzzleViews[index[1]].changeColor(puzzleViews[index[1]].NormalColor);
            puzzleViews[index[0]].changeColor(puzzleViews[index[0]].NormalColor);


            selectedViewsCounter = 0;
        }
    }

    private void EnableSwap()
    {
        for (int i = 0; i < numberOfWindows; i++)
        {
            views[viewOrder[i]].Swap = true;
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
        StartCoroutine(PuzzleTaskSwap());

        yield return new WaitUntil(() => TaskDone);
        print("Task3 is finished");
    }


    public void DisableDrag()
    {
        foreach (PracticeView view in views)
        {
            view.GetComponent<XRGrabInteractable>().enabled = false;
            //view.GetComponent<BoxCollider>().enabled = false;
        }

        foreach (LayoutSocket socket in sockets)
        {
            socket.gameObject.SetActive(false);
        }
    }

    public void DisableDrag(PracticeView view, LayoutSocket socket)
    {
        view.GetComponent<XRGrabInteractable>().enabled = false;
        view.GetComponent<BoxCollider>().enabled = false;

        socket.gameObject.SetActive(false);
    }

    private void ExperimentSetup()
    {

        if (parent == null)
        {
            print("parent is null");
        }

        switch (parent.experiment)
        {
            case PracticeExperiments.Experiment.Exp1:
                print("Exp1 selected");
                DisableDrag();
                StartCoroutine(Task1());
                break;
            case PracticeExperiments.Experiment.Exp2:
                print("Exp2 selected");
                DisableDrag();
                StartCoroutine(Task2());
                break;
            case PracticeExperiments.Experiment.Exp3:
                DisableDrag();
                EnableSwap();
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
    
    private void Update()
    {
        if (parent.experiment == PracticeExperiments.Experiment.Exp3)
            SwapTwoViewsSelected();
    }
}
