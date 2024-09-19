using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class PracticeView : MonoBehaviour, ISelectHandler, IDeselectHandler
{
    private PracticeTaskManagement parent;
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
        parent = GetComponentInParent<PracticeTaskManagement>();
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

    public void OnSelect(BaseEventData eventData)
    {
        if (swap && isSelected)
        {
            DisableInteraction();
        }

        if (swap & IsOn && !isSelected)
        {
            isSelected = true;
            StartCoroutine(WaitUntilOff());
            //print("view clicked. Disable now?");
            parent.SelectedViewsCounter++;
        }
    }

    public void OnDeselect(BaseEventData eventData)
    {
        if (swap)
        {
            TurnOn(true, true);
            if (parent.SelectedViewsCounter == 1)
                changeColor(selectedColor);
        }
        print("Got deselected?");
    }

    IEnumerator WaitUntilOff()
    {
        yield return new WaitUntil(() => !IsOn);

        //print("view is now off");
        DisableInteraction();
    }

}
