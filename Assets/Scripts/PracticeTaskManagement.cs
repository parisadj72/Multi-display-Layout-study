using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;

public class PracticeTaskManagement : MonoBehaviour
{
    private List<View> views = new List<View>();
    private List<LayoutSocket> sockets = new List<LayoutSocket>();
    private PuzzleLayout puzzleLayout;
    private PracticeExperiments parent;

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
        //print("Icons: " + randomIcons.Count);
        RandomizeIcons();

        ExperimentSetup();
    }

    private void InitializeLayout()
    {
        parent = GetComponentInParent<PracticeExperiments>();
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

    IEnumerator RandomWindowOn()
    {
        GameObject.Find("CanvasText/Scroll View/Viewport/Content/Text").GetComponent<Text>().text = "Running....";

        for (int i = selections; i > 0; i--)
        {
            windowNumberOn = UnityEngine.Random.Range(0, numberOfWindows);
            //print("Number was: " + turnedOnWindow);

            views[windowNumberOn].TurnOn(true, true);
            //print("Window on is: " + (turnedOnWindow + 1));

            yield return new WaitUntil(() => !views[windowNumberOn].IsOn);
        }

        GameObject.Find("CanvasText/Scroll View/Viewport/Content/Text").GetComponent<Text>().text = "Done.";

        TaskDone = true;
    }

    IEnumerator RandomWindowsOn()
    {
        GameObject.Find("CanvasText/Scroll View/Viewport/Content/Text").GetComponent<Text>().text = "Running....";
        GameObject.Find("Canvas/Scroll View/Viewport/Experiment2/Text").GetComponent<Text>().text = "Wait... \n Memorize the views that are on.";
        
        selections = (numberOfWindows / 3) + 1;

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].TurnOn(true, false);

        yield return new WaitForSeconds(5);

        GameObject.Find("Canvas/Scroll View/Viewport/Experiment2/Text").GetComponent<Text>().text = "Ok... \n Now Select the views that were on before, as fast as possible.";

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].TurnOn(false, true);


        for (int i = 0; i < selections; i++)
        {
            yield return new WaitUntil(() => checkAllOnDisableOns(views, viewOrder));
        }

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].DisableInteraction();

        GameObject.Find("CanvasText/Scroll View/Viewport/Content/Text").GetComponent<Text>().text = "Done.";

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
        GameObject.Find("CanvasText/Scroll View/Viewport/Content/Text").GetComponent<Text>().text = "Running....";
        selections = (numberOfWindows / 3) + 1;

        for (int i = 0; i < selections; i++)
            views[viewOrder[i]].TurnOn(true, false);

        yield return new WaitForSeconds(2);

        for (int i = 0; i < views.Count; i++)
        {
            if (!views[i].IsOn)
            {
                DisableDrag(views[i], sockets[i]);
            }
        }

        yield return new WaitForSeconds(3);

        foreach (LayoutSocket socket in sockets)
        {
            print(socket.LastIcon);
        }

        foreach (View v in puzzleLayout.Views)
        {
            print(v.RawIcon.texture.name);
        }

        yield return new WaitUntil(() => CheckIcons(sockets, puzzleLayout));

        GameObject.Find("CanvasText/Scroll View/Viewport/Content/Text").GetComponent<Text>().text = "Done.";
        TaskDone = true;
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
        StartCoroutine(KeepRandomOn());
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

    public void DisableDrag(View view, LayoutSocket socket)
    {
        view.GetComponent<XRGrabInteractable>().enabled = false;
        view.GetComponent<BoxCollider>().enabled = false;

        socket.gameObject.SetActive(false);
    }

    private bool CheckIcons(List<LayoutSocket> layoutSockets, PuzzleLayout puzzleLayout)
    {
        List<View> viewsList = puzzleLayout.Views;
        for (int i = 0; i < layoutSockets.Count; i++)
        {
            if (!views[i].IsOn || (layoutSockets[i].LastIcon.Equals(viewsList[i].RawIcon.texture.name) && layoutSockets[i].GetComponent<XRSocketInteractor>().hasSelection))
            {
                continue;
            }
            else return false;
        }
        return true;
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
                CanvasControl(true, false, false);
                print("Exp1 selected");
                DisableDrag();
                StartCoroutine(Task1());
                break;
            case PracticeExperiments.Experiment.Exp2:
                CanvasControl(false, true, false);
                print("Exp2 selected");
                DisableDrag();
                StartCoroutine(Task2());
                break;
            case PracticeExperiments.Experiment.Exp3:
                CanvasControl(false, false, true);
                print("Exp3 selected");
                puzzleLayout.gameObject.SetActive(true);
                StartCoroutine(Task3());
                break;

            default:
                print("got copied?");
                break;
        }
    }

    private void CanvasControl(bool Exp1, bool Exp2, bool Exp3)
    {
        GameObject.Find("Canvas/Scroll View/Viewport/Experiment1").SetActive(Exp1);
        GameObject.Find("Canvas/Scroll View/Viewport/Experiment2").SetActive(Exp2);
        GameObject.Find("Canvas/Scroll View/Viewport/Experiment3").SetActive(Exp3);
    }
}
