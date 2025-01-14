using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.UI;
using TMPro;

public class TaskManagement : MonoBehaviour
{
    private List<View> views = new List<View>();
    private List<LayoutSocket> sockets = new List<LayoutSocket>();
    private List<View> puzzleViews = new List<View>();
    private PuzzleLayout puzzleLayout;
    private Experiments parent;

    private List<Texture2D> textures = new List<Texture2D>();
    private List<int> randomIcons;

    private List<int> viewOrder;

    private int numberOfWindows;
    private int windowNumberOn;
    public int task1Selections = 5;
    public int selections = 5;

    private int selectedViewsCounter = 0;

    private int numberOfSwaps = 0;
    private float swapTime = 0.0f;

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
    public int SelectedViewsCounter { get => selectedViewsCounter; set => selectedViewsCounter = value; }

    private GameObject userPrompt;
    public GameObject UserPrompt { get => userPrompt; set => userPrompt = value; }
    public int NumberOfSwaps { get => numberOfSwaps; set => numberOfSwaps = value; }

    private void Awake()
    {
        InitializeLayout();
    }

    private void Start()
    {
        userPrompt = GameObject.FindGameObjectWithTag("PromptText");
        InitializeIconList();
        viewOrder = RandomGenerator.randomizeList(numberOfWindows);
        randomIcons = RandomGenerator.randomizeList(numberOfWindows);
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

    public bool IsExp3()
    {
        return (parent.experiment == Experiments.Experiment.Exp3);
    }


    // This method is for task 1
    // It is meant to turn on one view at a time
    IEnumerator RandomWindowOn()
    {
        userPrompt.GetComponent<TextMeshPro>().text = "";

        for (int i = task1Selections; i > 0; i--)
        {
            windowNumberOn = UnityEngine.Random.Range(0, numberOfWindows);

            views[windowNumberOn].TurnOn();
            views[windowNumberOn].EnableInteraction();

            yield return new WaitUntil(() => !views[windowNumberOn].isOn());

            views[windowNumberOn].DisableInteraction();

            views[windowNumberOn].firstTimeLookedAtTimer = 0.0f;
            views[windowNumberOn].lookedAtTimer = 0.0f;

            views[windowNumberOn].flagViewLookedAt = false;
        }

        // show a hint to user that all views has been selected
        userPrompt.GetComponent<TextMeshPro>().text = "Well Done!";

        TaskDone = true;
    }

    IEnumerator RandomWindowsOn()
    {
        userPrompt.GetComponent<TextMeshPro>().text = "";

        GameObject left = GameObject.FindGameObjectWithTag("LeftRay");
        GameObject right = GameObject.FindGameObjectWithTag("RightRay");

        XRInteractorLineVisual leftRay = left.GetComponent<XRInteractorLineVisual>();
        XRInteractorLineVisual rightRay = right.GetComponent<XRInteractorLineVisual>();

        leftRay.enabled = false;
        rightRay.enabled = false;

        for (int i = 0; i < selections; i++)
        {
            views[viewOrder[i]].TurnOn();
            views[viewOrder[i]].DisableInteraction();
        }

        float waitTime = selections;
        yield return new WaitForSeconds(waitTime);

        leftRay.enabled = true;
        rightRay.enabled = true;

        for (int i = 0; i < selections; i++)
        {
            views[viewOrder[i]].TurnOff();
            views[viewOrder[i]].EnableInteraction();
        }


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

    private bool checkAllOnDisableOns(List<View> views, List<int> viewOrder)
    {
        for (int i = 0; i < selections; i++)
            if (views[viewOrder[i]].isOn())
            {
                views[viewOrder[i]].DisableInteraction();

                views[viewOrder[i]].firstTimeLookedAtTimer = 0.0f;
                views[viewOrder[i]].lookedAtTimer = 0.0f;
                views[viewOrder[i]].flagViewLookedAt = false;
            }
        for (int i = 0; i < selections; i++)
        {
            if (views[viewOrder[i]].isOn())
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
            puzzleViews[i].TurnOn();
            puzzleViews[i].EnableInteraction();
        }

     /*   for (int i = 0; i < views.Count; i++)
        {
            if (!views[i].isOn())
            {
                DisableDrag(views[i], sockets[i]);
                views[i].GetComponent<TrackedDeviceGraphicRaycaster>().enabled = false;
            }
        }*/

        //yield return new WaitUntil(() => TwoViewsSelected());

        yield return new WaitUntil(() => CpompareIcons(puzzleLayout));

        TaskDone = true;
    }

    private bool CpompareIcons(PuzzleLayout puzzleLayout)
    {
        for (int i = 0; i < puzzleViews.Count; i++)
        {
            if (!puzzleViews[i].isOn() || (puzzleViews[i].RawIcon.texture.name.Equals(puzzleLayout.TexlistOns[i].name)))
            {
                continue;
            }
            else return false;
        }
        
        for(int i = 0; i < puzzleViews.Count; i++)
        {
            puzzleViews[i].DisableInteraction();
        }

        return true;
    }
    private void SwapTwoViewsSelected()
    {
        if (selectedViewsCounter == 2)
        {
            numberOfSwaps++;
            List<Texture> images = new List<Texture>();
            List<int> index = new List<int>();

            for (int i = 0; i < puzzleViews.Count; i++)
            {
                if (puzzleViews[i].isSelected)
                {
                    images.Add(puzzleViews[i].RawIcon.texture);
                    index.Add(i);
                    puzzleViews[i].isSelected = false;
                }
            }
            // now swap..
            puzzleViews[index[0]].RawIcon.texture = images[1];
            puzzleViews[index[1]].RawIcon.texture = images[0];
            puzzleViews[index[1]].changeColor(puzzleViews[index[1]].NormalColor);
            puzzleViews[index[0]].changeColor(puzzleViews[index[0]].NormalColor);

            System.IO.File.AppendAllText(GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().timerFilePath, "Time per swap = " + swapTime + "\n \n");
            swapTime = 0;
            
            selectedViewsCounter = 0;
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
        foreach (View view in views)
        {
            view.GetComponent<XRGrabInteractable>().enabled = false;
            //view.GetComponent<BoxCollider>().enabled = false;
        }

        foreach (LayoutSocket socket in sockets)
        {
            socket.gameObject.SetActive(false);
        }
    }

    public void DisableDrag(View view, LayoutSocket socket)
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
                DisableDrag();
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
        if (parent.experiment == Experiments.Experiment.Exp3)
        {
            SwapTwoViewsSelected();
            swapTime += Time.deltaTime;
        }
    }
}
