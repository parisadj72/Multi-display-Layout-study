using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;
using static Unity.VisualScripting.Metadata;

public class View : MonoBehaviour, ISelectHandler
{
    private Toggle toggle;
    private string icon;
    private RawImage rawIcon;

    private Boolean isOn;
    private Boolean isInteractable;

    public Boolean disabledAtStartup = true;

    private void Awake()
    {
        InitializeView();

        if (disabledAtStartup)
        {
            DisableInteraction();
        }
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

    private void InitializeView()
    {
        toggle = GetComponent<Toggle>();

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
                rawIcon = child.GetComponentInChildren<RawImage>();
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

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }

    public void OnSelect(BaseEventData eventData)
    {
        if (IsOn)
        {
            //print("view clicked. Disable now?");
            StartCoroutine(WaitUntilOff());
        }
    }

    IEnumerator WaitUntilOff()
    {
        yield return new WaitUntil(() => !IsOn);

        //print("view is now off");
        DisableInteraction();
    }
}
