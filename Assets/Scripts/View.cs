using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using TMPro;
using static Experiments;

public class View : MonoBehaviour, ISelectHandler, IDeselectHandler, IPointerClickHandler
{
    private TaskManagement parent;
    private Toggle toggle;
    private string icon;
    private RawImage rawIcon;
    private Color selectedColor;
    private Color normalColor;

    private GameObject on;

    private Boolean isOn;
    private Boolean isInteractable;
    private bool swap = false;
    private bool isSelected = false;

    public Boolean disabledAtStartup = true;

    public bool flagViewLookedAt = false;
    public float firstTimeLookedAtTimer = 0.0f;
    public float lookedAtTimer = 0.0f;
    //public bool flagViewSelected = false;


    private float wrongClickCounter = 0;
    private float localSelectedTimer = 0.0f;


    public float WrongClickCounter
    {
        get { return wrongClickCounter; }
        set { wrongClickCounter = value; }
    }

    public Toggle Toggle
    {
        get { return toggle; }
        set { toggle = value; }
    }

    public Boolean IsOn
    {
        get { return isOn; }
        set { isOn = value; }
    }

    public string Icon
    {
        get { return icon; }
        set { icon = value; }
    }

    public RawImage RawIcon
    {
        get { return rawIcon; }
        set { rawIcon = value; }
    }

    public Color SelectedColor { get => selectedColor; set => selectedColor = value; }
    public Color NormalColor { get => normalColor; set => normalColor = value; }
    public bool Swap { get => swap; set => swap = value; }
    public bool IsSelected { get => isSelected; set => isSelected = value; }

    private void Awake()
    {
        InitializeView();

        if (disabledAtStartup)
        {
            DisableInteraction();
        }
    }

    private void InitializeView()
    {
        parent = GetComponentInParent<TaskManagement>();
        toggle = GetComponent<Toggle>();
        selectedColor = toggle.colors.pressedColor;

        //icon = GetImage();
        //print(icon);
        isInteractable = toggle.interactable;
        IsOn = toggle.isOn;

        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            //print(child.gameObject);
            if (child.gameObject.name == "On")
            {
                on = child.gameObject;
                rawIcon = child.GetComponentInChildren<RawImage>();
                normalColor = child.GetComponent<Image>().color;
                //print(rawImage.texture);
            }
        }
    }
    public void SetStatus()
    {
        IsOn = toggle.isOn;
    }

    public void TurnOn(Boolean isOn, bool enableInteraction)
    {
        IsOn = isOn;
        toggle.interactable = enableInteraction;
        toggle.isOn = isOn;
        //flagViewSelected = false;
        //print("Interaction enabled: " + toggle.interactable);
    }


    public string GetImage()
    {
        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            //print(child.gameObject);
            if (child.gameObject.name == "On")
            {
                rawIcon = child.GetComponentInChildren<RawImage>();
                //print(rawImage.texture);
            }
        }
        return rawIcon.texture.name;
    }

    public void SetImage(string image)
    {
        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            //print(child.gameObject);
            if (child.gameObject.name == "On")
            {
                rawIcon = child.GetComponentInChildren<RawImage>();
                //print(rawImage.texture);
            }
        }
    }

    public void changeColor(Color color)
    {
        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            //print(child.gameObject);
            if (child.gameObject.name == "On")
            {
                child.gameObject.GetComponent<Image>().color = color;
            }
        }
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }

    public void EnableInteraction()
    {
        toggle.interactable = true;
    }

    public void OnSelect(BaseEventData eventData)
    {
        //flagViewSelected = true;
        //flagViewLookedAt = false;

        /*if (IsOn) {
            *//*//write time per selection for each view into the prompt
            parent.UserPrompt.GetComponent<TextMeshPro>().text = "Time per selection = " + localSelectedTimer;*//*

            System.IO.File.AppendAllText(GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().timerFilePath, "Time per selection = " + localSelectedTimer + "\n \n");
            localSelectedTimer = 0;
        }

        if (swap && isSelected)
        {
            DisableInteraction();
        }

        if (isOn && !isSelected)
        {
            isSelected = true;
            //StartCoroutine(WaitAndOff());
            //print("view clicked. Disable now?");
            parent.SelectedViewsCounter++;
        }*/
        if (swap)
        {
            if (isOn && !isSelected)
            {
                isSelected = true;
                StartCoroutine(WaitAndOff());
                parent.SelectedViewsCounter++;
            }
            else
                DisableInteraction();
        }
    }

    public void OnDeselect(BaseEventData eventData)
    {
        if (swap)
        {
            TurnOn(true, true);
            if (parent.SelectedViewsCounter == 1)
                changeColor(selectedColor);
            print("Got deselected?");
        }
    }

    IEnumerator WaitAndOff()
    {
        yield return new WaitUntil(() => !isOn);
        //yield return new WaitForEndOfFrame();
        TurnOn(true, false);
        //DisableInteraction();
    }

    public void OnPointerClick(PointerEventData eventData)
    {
        if (!toggle.interactable)
        {
            wrongClickCounter++;
        }
        if (toggle.interactable && GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().experiment != Experiment.Exp3)
        {
            System.IO.File.AppendAllText(GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().timerFilePath, "Time per selection = " + localSelectedTimer + "\n \n");
            localSelectedTimer = 0;
        }
    }
    private void Update()
    {
        if (GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().experiment == Experiment.Exp1 && IsOn)
        {
            firstTimeLookedAtTimer += Time.deltaTime;
            lookedAtTimer += Time.deltaTime;
            localSelectedTimer += Time.deltaTime;
        }
        if(GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().experiment == Experiment.Exp2 && !IsOn && toggle.interactable)
        {
            firstTimeLookedAtTimer += Time.deltaTime;
            lookedAtTimer += Time.deltaTime;
            localSelectedTimer += Time.deltaTime;
        }
    }
}
